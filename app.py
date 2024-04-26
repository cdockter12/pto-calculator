from datetime import datetime
from urllib import request
from flask import Flask, render_template, request
from jinja2 import Template

app = Flask(__name__)


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        pto_mod = request.form.get("addhours")
        formatted_date = datetime.today().strftime("%Y-%m-%d")
        print(pto_mod, formatted_date)
    return render_template("home.html", name="Cole")


@app.route('/login/')
def login():
    return render_template("auth/login.html")


@app.route('/register/')
def register():
    return render_template("auth/register.html")
