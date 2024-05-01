import smtplib
import os
from email.mime.text import MIMEText
from db.models import db, Users, Pto
from flask_apscheduler import APScheduler


def init_controllers(app):
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

    # @scheduler.task('cron', id='fetch_pto', day='last')
    @scheduler.task('interval', id='test_schedule', seconds=10)
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
