from flask import render_template, redirect, url_for
from app import app


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index():
    return render_template("nonogen.html")
