from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import mysql.connector as mysql

mysql_connection = mysql.connect(
    host="localhost",
    user="root",
    passwd="",
    database="db_kompol"
)

cursor = mysql_connection.cursor(buffered=True)

app = Flask(__name__)


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

        
        cursor.execute("INSERT INTO users (nama_user, email_user, password) VALUES (%s,%s,%s)",
                    (name, email, hash_password))
        mysql_connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('dashboard/index.html'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cursor.execute("SELECT * FROM users WHERE email_user=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
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
    app.secret_key = b'\xf5q\xea0\xb5R'
    app.run(debug=True)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard/index.html')


@app.route("/forum")
def forum():
    return render_template('forum/index.html')


@app.route("/forum/thread")
def thread():
    return render_template('forum/thread.html')


@app.route("/laporankunjungan")
def laporankunjungan():
    return render_template('laporankunjungan/index.html')
