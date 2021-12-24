from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/forum")
def forum():
    return render_template('forum/index.html')


@app.route("/forum/thread")
def thread():
    return render_template('forum/thread.html')


@app.route("/laporankunjungan")
def laporankunjungan():
    return render_template('laporankunjungan/index.html')


@app.route("/info")
def info():
    return render_template('info/index.html')
