from flask import Blueprint, render_template, request, redirect
from flask_login import current_user
from flask import current_app as app
from flask_login import login_required


main_bp = Blueprint('main_bp', __name__,
                    template_folder='templates',
                    static_folder='static')


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/secure', methods=['GET', 'POST'])
@login_required
def secure():
    return render_template('secure.html')
