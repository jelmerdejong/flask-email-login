from time import time
from flask import current_app
import jwt
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)
    email = db.Column(db.String(320),
                      nullable=False,
                      unique=True)
    created_on = db.Column(db.DateTime,
                          index=False,
                          unique=False,
                          nullable=True)
    last_login = db.Column(db.DateTime,
                           index=False,
                           unique=False,
                           nullable=True)

    def get_login_token(self, expires_in=600):
        return jwt.encode(
            {'login_token': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_login_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['login_token']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.email)
