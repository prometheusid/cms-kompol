from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
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
app.secret_key = '\x0c,\x99\xd9\x8d\x01M\xa8B\xcb+\x9d\x9ee\x95M}\xfe8YMW\x1a\xb6'


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/registrasi", methods=["GET", "POST"])
def registrasi():
    if request.method == 'GET':
        return render_template('registrasi/index.html')
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
        return redirect(url_for('dashboard/index.html'))


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
                return render_template("dashboard/index.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login/index.html")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    app.run()


@app.route("/dashboard")
def dashboard():
    return render_template('dashboard/index.html')


# Forum
@app.route("/forum")
def forum():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from tbl_forum")
    data = cur.fetchall()
    return render_template('forum/index.html', data=data)


@app.route("/forum/forumdashboard")
def forumdashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from tbl_forum")
    data = cur.fetchall()
    return render_template('forum/forum.html', data=data)


@app.route("/forum/tambah", methods=["GET", "POST"])
def tambahforum():
    if request.method == 'GET':
        return render_template('forum/tambahbaru.html')
    else:
        idForum = request.form['idForum']
        judulForum = request.form['judulForum']
        isi = request.form['content']
        ts = session['id']
        waktu = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_forum (forum_id, forum_judul, forum_isi, created_by, created_at) VALUES (%s,%s,%s,%s,%s)",
                    (idForum, judulForum, isi, ts, waktu))
        mysql.connection.commit()
        return render_template('forum/forum.html')


@app.route("/forum/thread/<int:id>", methods=["GET"])
def thread(id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * from tbl_forum WHERE forum_id=%s""", (id,))
    forum = cur.fetchall()
    return render_template('forum/thread.html', forum=forum)


@app.route("/forum/threads/<int:id>", methods=["GET"])
def threads(id):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * from tbl_forum WHERE forum_id=%s""", (id,))
    forum = cur.fetchall()
    return render_template('forum/threads.html', forum=forum)

# Laporan Kunjungan


@app.route("/laporankunjungan")
def laporankunjungan():
    return render_template('laporankunjungan/index.html')


@app.route("/laporankunjungan/tambahlaporankunjungan")
def tambahlaporankunjungan():
    return render_template('laporankunjungan/tambahlaporankunjungan.html')


@app.route("/info/")
def info():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM info")
    data = cur.fetchall()
    return render_template('info/index.html', data=data)


@app.route("/info/tambahinfo", methods=["GET", "POST"])
def tambahinfo():
    if request.method == 'GET':
        return render_template('info/tambahinfo.html')
    else:
        author = session['id']
        penulis = session['name']
        judul = request.form['judul-info']
        isi = request.form['isi-info']
        waktu = datetime.now()
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO info (user_id, judul_info, isi_info, created_at, penulis) VALUES (%s,%s,%s,%s, %s)",
                    (author, judul, isi, waktu, penulis))
        mysql.connection.commit()

    return render_template('/info/tambahinfo.html')


@app.route("/info/detail/<id>")
def detail(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM info WHERE info_id=%s", (id,))
    data = cur.fetchone()
    return render_template('info/detailinfo.html', data=data)
