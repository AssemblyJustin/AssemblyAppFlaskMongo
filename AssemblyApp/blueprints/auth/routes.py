from flask import render_template, redirect, url_for, flash, request, abort
from . import auth
from .forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from flask_login import login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
from models.user import User
import uuid

@auth.route('/register/<invitation_token>', methods=['GET', 'POST'])
def register(invitation_token):
    user_data = mongo.db.users.find_one({'invitation_token': invitation_token})
    if not user_data:
        flash('Invalid or expired invitation token.', 'danger')
        return redirect(url_for('auth.login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data)
        mongo.db.users.update_one(
            {'_id': user_data['_id']},
            {
                '$set': {
                    'username': form.username.data,
                    'password_hash': password_hash,
                    'invitation_token': None,
                    'is_active': True
                }
            }
        )
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.projects'))

    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({'username': form.username.data})
        if user_data and check_password_hash(user_data['password_hash'], form.password.data):
            user = User(user_data)
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.projects'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/invite', methods=['GET', 'POST'])
@login_required
def invite():
    if not current_user.is_admin():
        abort(403)
    if request.method == 'POST':
        email = request.form.get('email')
        assigned_projects = request.form.getlist('assigned_projects')
        invitation_token = str(uuid.uuid4())
        mongo.db.users.insert_one({
            'email': email,
            'assigned_projects': assigned_projects,
            'invitation_token': invitation_token,
            'is_active': False,
            'role': 'engineer'
        })
        invitation_link = url_for('auth.register', invitation_token=invitation_token, _external=True)
        flash(f'Invitation link: {invitation_link}', 'info')
        # In a real application, you would send the invitation_link via email
    projects = mongo.db.projects.find()
    return render_template('invite.html', projects=projects)