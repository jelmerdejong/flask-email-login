from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail
from flask import render_template, current_app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_login_token_email(user):
    token = user.get_login_token()
    send_email(('Log In Token'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/login.txt',
                                         user=user, token=token),
               html_body=render_template('email/login.html',
                                         user=user, token=token))
