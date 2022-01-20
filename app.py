from turtle import title
from flask import Flask, render_template, request, session, url_for, make_response
import bcrypt
from flask.typing import TemplateFilterCallable
from werkzeug.utils import redirect
from werkzeug.wrappers import response
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+MySQLdb://root:@localhost/db_kompol'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_kompol'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'


# @app.route("/")
# def pub_home():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM info ORDER BY info_id DESC LIMIT 1")
#     data = cur.fetchone()
#     return render_template('/public/index.html', data=data)


@app.route("/")
def pub_home():
    title = ("KOMUNIKASI POLITIK")
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM info ORDER BY info_id DESC LIMIT 1")
    info = cur.fetchone()
    cur.execute("SELECT * FROM tbl_forum ORDER BY forum_id DESC LIMIT 1")
    data = cur.fetchone()
    return render_template('/public/index.html', data=data, info=info, title=title)


@app.route("/registrasi", methods=["GET", "POST"])
def registrasi():
    if request.method == 'GET':
        return render_template('public/pub_login/registrasi.html')
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (nama_user, email_user, password) VALUES (%s,%s,%s)",
                    (name, email, hash_password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('pub_home'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email_user=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['id'] = user['user_id']
                session['name'] = user['nama_user']
                session['email'] = user['email_user']
                session['role'] = user['role_id']
                # return render_template("/public/index.html")
                if user['role_id'] == 0:
                    return redirect(url_for('pub_home'))
                if user['role_id'] == 1:
                    return redirect(url_for('pub_home'))

            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("/public/pub_login/login.html")


@app.route('/logout')
def logout():
    session.clear()
    # return render_template("/public/index.html")
    return redirect(url_for('pub_home'))


@app.route("/pub_forum")
def public_forum():
    title = ("FORUM DISKUSI")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * from tbl_forum as a JOIN users as b ON a.user_id = b.user_id WHERE b.user_id ORDER BY created_at DESC")
    data = cur.fetchall()
    return render_template('/public/pub_forum/index.html', data=data, title=title)


@app.route("/pub_forum/thread/<int:id>")
def thread(id):
    title = ("FORUM DISKUSI")
    # if request.method == 'GET':
    # Get one data forum
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from tbl_forum as a \
                    LEFT JOIN tbl_detail_forum as b ON a.forum_id = b.forum_id \
                    LEFT JOIN users as c ON a.user_id = c.user_id WHERE a.forum_id=%s", (id,))
    data = cur.fetchone()

    # Get Count commentar
    count = mysql.connection.cursor()
    count.execute(
        "SELECT count('forum_id') FROM tbl_detail_forum  WHERE forum_id=%s", (id,))
    counting = count.fetchone()

    # Get data commentar
    com = mysql.connection.cursor()
    com.execute(
        "SELECT * FROM tbl_detail_forum as a JOIN users as b ON a.user_id = b.user_id WHERE a.forum_id=%s", (id,))
    comment = com.fetchall()
    return render_template('/public/pub_forum/thread.html', data=data, comment=comment, counting=counting,  title=title)
    # else:
    #   idKomen = request.form['idKomen']
    #  idForum = request.form['idForum']
    # komen = request.form['komen']
    #   komenUser = session['id']
    #   waktu = datetime.now()
    #  cur = mysql.connection.cursor()
    #  cur.execute("INSERT INTO tbl_detail_forum (id_detail_forum, forum_id, komentar, user_id, created_at) VALUES (%s,%s,%s,%s,%s)",
    #             (idKomen, idForum, komen, komenUser, waktu))
    # mysql.connection.commit()
    # return redirect(url_for('/public/pub_forum/thread.html', title=title))


@app.route("/pub_forum/thread", methods=["POST"])
def komentar():
    idKomen = request.form['idKomen']
    idForum = request.form['idForum']
    komen = request.form['komen']
    komenUser = session['id']
    waktu = datetime.now()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tbl_detail_forum (id_detail_forum, forum_id, komentar, user_id, created_at) VALUES (%s,%s,%s,%s,%s)",
                (idKomen, idForum, komen, komenUser, waktu))
    mysql.connection.commit()
    return redirect(request.referrer)


@app.route("/pub_forum/tambah", methods=["GET", "POST"])
def tambahforum():
    title = ("FORUM DISKUSI")
    if request.method == 'GET':
        return render_template('public/pub_forum/tambahforum.html', title=title)
    else:
        idForum = request.form['idForum']
        judulForum = request.form['judulForum']
        isi = request.form['content']
        ts = session['id']
        waktu = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_forum (forum_id, forum_judul, forum_isi, user_id, created_at) VALUES (%s,%s,%s,%s,%s)",
                    (idForum, judulForum, isi, ts, waktu))
        mysql.connection.commit()
    return render_template('public/pub_forum/index.html', title=title)


@app.route("/pub_forum/update/<int:id>", methods=["GET", "POST"])
def updateforum(id):
    title = ("FORUM DISKUSI")
    if request.method == "GET":
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from tbl_forum WHERE forum_id=%s", (id,))
        data = cur.fetchone()
        return render_template('public/pub_forum/update.html', data=data, title=title)
    else:
        return render_template("public/pub_forum/thread/%s", (id))


@app.route("/pub_forum/simpanupdate/<int:id>", methods=["GET", "POST"])
def simpanupdate(id):
    if request.method == "POST":
        fid = request.form['idForum']
        judulForum = request.form['judulForum']
        isi = request.form['content']
        waktu = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tbl_forum SET forum_judul = %s, forum_isi = %s, user_id = %s, created_at = %s WHERE forum_id = %s",
                    (judulForum, isi, waktu, fid))
        mysql.connection.commit()
        return redirect(url_for('public_forum'))
    else:
        title = ("FORUM DISKUSI")
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from tbl_forum WHERE forum_id=%s", (id,))
        data = cur.fetchone()
        return render_template("public/pub_forum/thread.html", data=data, title=title)


@app.route('/pub_info')
def public_info():
    title = ("INFO PUBLIK")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * from info as a JOIN users as b ON a.user_id = b.user_id WHERE b.user_id ORDER BY created_at DESC")
    data = cur.fetchall()
    return render_template('/public/pub_info/index.html', data=data, title=title)


@app.route('/pub_info/detail/<int:id>')
def detail(id):
    title = ("INFO PUBLIK")
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * from info as a LEFT JOIN users as b ON a.user_id = b.user_id WHERE a.info_id=%s", (id,))
    data = cur.fetchone()
    return render_template('/public/pub_info/detail.html', data=data, title=title)


@app.route("/pub_info/tambahinfo", methods=["GET", "POST"])
def tambahinfo():
    title = ("INFO PUBLIK")
    if request.method == 'GET':
        return render_template('/public/pub_info/tambahinfo.html', title=title)
    else:
        author = session['id']
        judul = request.form['judul-info']
        isi = request.form['isi-info']
        waktu = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO info (user_id, judul_info, isi_info, created_at) VALUES (%s,%s,%s,%s)",
                    (author, judul, isi, waktu))
        mysql.connection.commit()
    return render_template('/public/pub_info/tambahinfo.html', title=title)


@app.route("/pub_laporankunjungan/")
def public_lapkun():
    title = ('LAPORAN KUNJUNGAN')
    return render_template('/public/pub_lapkun/index.html', title=title)


# dashboard / cpanel admin
@app.route("/dashboard/")
def dashboard():
    user_role = session['role']
    if user_role == 0:
        return render_template('/dashboard/cp_base.html')
    else:
        return redirect(url_for('pub_home'))


@app.route("/dashboard/cp_forum")
def cp_forum():
    title = ('FORUM')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_forum")
    data = cur.fetchall()
    return render_template('/dashboard/cp_forum/index.html', data=data, title=title)


@app.route("/dashboard/cp_forum/delete/<int:id>")
def hapus_forum(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tbl_forum WHERE forum_id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('cp_forum'))


@app.route('/dashboard/cp_info')
def cp_info():
    title = ('INFO PUBLIK')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM info")
    data = cur.fetchall()
    return render_template('/dashboard/cp_info/index.html', data=data, title=title)


@app.route("/dashboard/cp_info/delete/<int:id>")
def hapus_info(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM info WHERE info_id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('cp_info'))


@app.route("/dashboard/cp_lapkun")
def cp_lapkun():
    title = ('LAPORAN KUNJUNGAN')
    return render_template('/dashboard/cp_lapkun/index.html', title=title)
