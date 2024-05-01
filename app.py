import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from urllib import request
from flask import Flask, render_template, request, session, flash, redirect, url_for, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError

from db.models import db, Users, Pto
from db.session import generate_db_conn_string
from flask_apscheduler import APScheduler


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = generate_db_conn_string()
    app.secret_key = os.environ['SECRET_KEY']

    # Initialize DB and create our tables.
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize our background scheduler for auto-updating PTO balances.
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    def send_email_update(input_msg, recipient):
        """
        This function sends an email to the recipient when their PTO balance is modified by the scheduler.
        :param: input_msg: String - the message we want to send to the recipient.
        :param: recipient: String - the email address of the recipient.
        """
        sender = os.environ['MAIL_USERNAME']
        password = os.environ['MAIL_PASSWORD']
        recipients = [recipient]
        msg = MIMEText(input_msg)
        msg['Subject'] = "Your Current PTO Balance Has Been Updated"
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()

    @scheduler.task('cron', id='fetch_pto', day='last')
    # @scheduler.task('interval', id='test_schedule', seconds=5)
    def update_pto_on_pay_period():
        """
        This function updates all users pto balance in the database on the last day of the month, then calls a function
        to send an email update to the user notifying them that their pto balance has changed.
        :return: None
        """
        with scheduler.app.app_context():
            # Grab all users
            users = db.session.query(Users).all()
            # This continually selects the first row and doesn't execute again. Why?
            for user in users:
                # Check for is_senior flag
                if user.is_senior == 1:
                    # 4 wks / year
                    pto_mod = 20 / 12
                else:
                    # 3 wks / year
                    pto_mod = 15 / 12
                pto = db.session.query(Pto).filter(Pto.user_id == user.id and Pto.is_current is True).first()
                pto.pto_balance += pto_mod
                # Send user an email w/ current pto
                input_msg = f"Dear {user.email}, a pay period has passed! Your current PTO balance is now {pto.pto_balance} hrs."
                send_email_update(input_msg, user.email)

            db.session.commit()

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

    return app
