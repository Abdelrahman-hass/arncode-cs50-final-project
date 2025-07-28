from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_email(to, subject, body):
    msg = Message(subject, recipients=[to], body=body, sender=current_app.config["MAIL_USERNAME"])
    mail.send(msg)