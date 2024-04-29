from datetime import datetime
from urllib import request
from flask import Flask, render_template, request, session, flash, redirect, url_for
from passlib.hash import pbkdf2_sha256
from jinja2 import Template

app = Flask(__name__)

# Manually generate app secret key? Read about this more...
app.secret_key = "1awawet-kwetkmKEJTKET868-j-rP_weroWEOTIulkm"

users = {'cole@gmail.com': 12345,
         'pto_balance': 5}
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        pto_mod = request.form.get("addhours")
        formatted_date = datetime.today().strftime("%Y-%m-%d")
        # Database modification here
        print(pto_mod, formatted_date)
        if session.get("email"):
            # Add pto balance to params here, pass in on html file.
            users['pto_balance'] += pto_mod
        else:
            # If user is not logged in, what do we do with form input?
            flash("You must be logged in to do that!")
    if session.get("email"):
        return render_template("home.html", email=session.get("email"), pto=session.get("pto_balance"))
    else:
        return render_template("home.html", email="Guest", pto="?")



@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # print(email, password)
        # Check if our email & password match a record in our db. Verifying the password passed in from form with the properties from when it was hashed in DB.
        if pbkdf2_sha256.verify(password, users.get(email)):
            # Lets our browser know we have a valid and logged in user.
            session["email"] = email
            # pull this from database.
            # session['pto_balance'] = pto_balance

            flash("Login Successful!")
            return redirect(url_for('home'))
        else:
            flash("Login Failed. Please try again.")

    return render_template("auth/login.html")


@app.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = pbkdf2_sha256.hash(request.form.get("password"))
        pto_balance = request.form.get("pto_balance")

        # save to DB or users dict
        users[email] = password
        users[pto_balance] = pto_balance

        # Lets our browser know we have a valid and logged in user.
        session["email"] = email
        session["pto_balance"] = pto_balance

        flash("Registration Successful!")
        return redirect(url_for('login'))

    return render_template("auth/register.html")
