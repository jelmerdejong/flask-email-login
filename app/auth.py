from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask import current_app as app
from flask_login import current_user, login_user, logout_user
from .forms import LoginForm, SignupForm
from .models import db, User
from .email import send_login_token_email
from . import login_manager



auth_bp = Blueprint('auth_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_login_token_email(user)
            flash('The login link has been sent to your email')
        else:
            flash('Please sign up first')
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/login.html',
                           title='Login',
                           form=form)


@auth_bp.route('/login_token/<token>', methods=['GET', 'POST'])
def login_token(token):
    user = User.verify_login_token(token)
    if not user:
        flash('Invalid login link')
        return redirect(url_for('auth_bp.login'))
    login_user(user)
    return redirect(url_for('index'))


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if not form.validate_on_submit():
        print("not validated)")
        return render_template('auth/signup.html',
                               title='Sign Up',
                               form=form)
    print("form validated")
    try:
        print("try")
        user = User(email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('You are registered')
        return redirect(url_for('auth_bp.login'))
    except:
        print("except)")
        db.session.rollback()
        flash('An error occured during registration')
        return redirect(url_for('auth_bp.signup'))
    finally:
        db.session.close()



@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))
