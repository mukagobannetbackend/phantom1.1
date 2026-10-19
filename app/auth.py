from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from . import db
from .models import User

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower(); name = request.form.get('display_name','').strip(); password = request.form.get('password','')
        if not email or not name or len(password) < 8: flash('Use a name, valid email, and password of at least 8 characters.', 'error')
        elif User.query.filter_by(email=email).first(): flash('An account with that email already exists.', 'error')
        else:
            user = User(email=email, display_name=name); user.set_password(password); db.session.add(user); db.session.commit(); login_user(user); return redirect(url_for('main.dashboard'))
    return render_template('auth.html', mode='register')

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if user and user.check_password(request.form.get('password','')): login_user(user, remember=True); return redirect(request.args.get('next') or url_for('main.dashboard'))
        flash('Email or password not recognised.', 'error')
    return render_template('auth.html', mode='login')

@auth.route('/logout')
def logout(): logout_user(); return redirect(url_for('auth.login'))
