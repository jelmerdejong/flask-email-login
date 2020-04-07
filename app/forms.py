from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, Length


class SignupForm(FlaskForm):
    email = StringField(('Email'), validators=[Email(), DataRequired()])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[Length(min=6),
                        Email(message='Enter a valid email'),
                        DataRequired()])
    submit = SubmitField('Log In')
