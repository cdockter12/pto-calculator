import os
from datetime import datetime
from urllib import request
from flask import Flask, render_template, request, session, flash, redirect, url_for, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db.models import db, Users, Pto
from db.session import generate_db_conn_string
from jinja2 import Template


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = generate_db_conn_string()
    db.init_app(app)

    # Manually generate app secret key? Read about this more...
    app.secret_key = os.environ['SECRET_KEY']

    # Creates our tables in the DB
    with app.app_context():
        db.create_all()

    @app.route('/', methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            pto_mod = request.form.get("addhours")
            if session.get("email"):
                # Get old pto balance
                user = db.session.query(Users).filter(Users.email == session["email"]).first()
                pto = db.session.query(Pto).filter(Pto.user_id == user.id and Pto.is_current is True).first()
                current_pto = pto.pto_balance
                # Set the old PTO balance row is_current to 0
                pto.is_current = False
                # Create new PTO balance row with is_current to 1, preserving historical records.
                new_pto = Pto(pto_balance=(current_pto + float(pto_mod)), user_id=user.id, last_updated=datetime.now(), is_current=True)
                db.session.add(new_pto)
                db.session.commit()
                # Change session info for correct render after change
                session["pto_balance"] = new_pto.pto_balance
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

            # Query the user
            user = db.session.query(Users).filter(Users.email == email).first()

            # Check if our email & password match a record in our db. Verifying the password passed in from form with the properties from when it was hashed in DB.
            if pbkdf2_sha256.verify(password, user.password):
                # Lets our browser know we have a valid and logged in user.
                session["email"] = email

                # Grab PTO balance from the PTO table.
                pto = db.session.query(Pto).filter(Pto.user_id == user.id and Pto.is_current is True).first()
                session["pto_balance"] = pto.pto_balance

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
            is_senior = request.form.get("is_senior")

            # save to DB or users dict
            user = Users(email=email, password=password, is_senior=is_senior)
            try:
                db.session.add(user)
                db.session.commit()
                # Need to commit the user before PTO, so we can setup the foreign key constraint.
                pto = Pto(pto_balance=pto_balance, user_id=user.id, last_updated=datetime.now(), is_current=True)
                db.session.add(pto)
                db.session.commit()
            except SQLAlchemyError as e:
                # Add functionality for duplicate emails later?
                abort(500, message="An error occurred while registering the user.")

            # Lets our browser know we have a valid and logged in user. Displayed on home page.
            session["email"] = email
            session["pto_balance"] = pto_balance

            flash("Registration Successful!")
            return redirect(url_for('login'))

        return render_template("auth/register.html")

    return app
