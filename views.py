from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from urllib import request
from flask import render_template, request, session, flash, redirect, url_for, abort
from db.models import db, Users, Pto


def init_views(app):
    # Initialize DB and create our tables.
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route('/', methods=["GET", "POST"])
    def home():
        """
        Includes functionality for updating PTO balances. Also displays the current balance on the home page.
        :return: Home page with different data if session detects logged in user or not.
        """
        if request.method == "POST":
            if session.get("email"):
                # Get form hour amount
                pto_mod = request.form.get("addhours")
                # Get old pto balance
                user = db.session.query(Users).filter(Users.email == session["email"]).first()
                # Update PTO balance in place.
                pto = db.session.query(Pto).filter(Pto.user_id == user.id and Pto.is_current is True).first()
                pto.pto_balance += float(pto_mod)
                pto.last_update = datetime.now()

                # ---------------------------------------------- # Needs Work
                # Set the old PTO balance row is_current to False
                # pto.is_current = False

                # Create new PTO balance row with is_current to True, preserving historical records.
                # new_pto = Pto(pto_balance=(current_pto + float(pto_mod)), user_id=user.id, last_updated=datetime.now(), is_current=True)

                # db.session.add(new_pto)
                # ---------------------------------------------- #

                # Commit changes to DB.
                db.session.commit()
                # Change session info for correct render after change
                session["pto_balance"] = pto.pto_balance
            else:
                # If user is not logged in, display flash message.
                flash("You must be logged in to do that!")

        if session.get("email"):
            return render_template("home.html", email=session.get("email"), pto=session.get("pto_balance"))
        else:
            return render_template("home.html", email="Guest", pto="?")

    @app.route('/login/', methods=["GET", "POST"])
    def login():
        """
        Login route that sets up browser session & verifies user credentials with stored record in DB.
        :return: Home page if successful POST request, Login page if GET request.
        """
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            # Query the user
            user = db.session.query(Users).filter(Users.email == email).first()

            # Check if our email & password match a record in our db.
            # Verifying the password passed in from form with the properties from when it was hashed in DB.
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
        """
        Registers a new user in our database and sets initial PTO balance.
        :return: Redirect to login page or register if GET request.
        """
        if request.method == "POST":
            email = request.form.get("email")
            password = pbkdf2_sha256.hash(request.form.get("password"))
            pto_balance = request.form.get("pto_balance")
            is_senior = request.form.get("is_senior")

            # Create new user object with form data.
            user = Users(email=email, password=password, is_senior=is_senior)
            try:
                db.session.add(user)
                db.session.commit()
                # Need to commit the user before PTO, so we can set up the foreign key constraint.
                pto = Pto(pto_balance=pto_balance, user_id=user.id, last_updated=datetime.now(), is_current=True)
                db.session.add(pto)
                db.session.commit()
            except SQLAlchemyError as e:
                # Add notification for duplicate emails later?
                abort(500, message="An error occurred while registering the user.")

            # Lets our browser know we have a valid and logged-in user. Displayed on home page.
            session["email"] = email
            session["pto_balance"] = pto_balance

            flash("Registration Successful!")
            # We can optionally send an email verification here.
            return redirect(url_for('login'))

        return render_template("auth/register.html")

    @app.route("/logout")
    def logout():
        """
        Resets session data signifying a "logged out" user. Redirects to home page.
        :return: Redirect to home page.
        """
        if session.get("email"):
            session["email"] = None
        return redirect(url_for("home"))
