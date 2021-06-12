from uuid import uuid4

import praw
from project.constants import *
from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

auth = Blueprint('auth', __name__)

auth_r = praw.Reddit(client_id=CLIENT_ID,
								client_secret=CLIENT_SECRET,
								redirect_uri=REDIRECT_URI,
								user_agent=USER_AGENT)


@auth.route('/login')
def login():
	return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
	name = request.form.get('name')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False
	user = User.query.filter_by(name=name).first()
	if not user or not check_password_hash(user.password, password):
		flash('Please check your login details and try again.')
		return redirect(url_for('auth.login'))
	login_user(user, remember=remember)
	return redirect(url_for('auth.authorize'))


def save_created_state(state):
	User.query.filter_by(name=current_user.name).update({User.state:state}, synchronize_session = False)
	db.session.commit()

def is_valid_state(state):
	saved_state = User.query.filter_by(name=current_user.name).first().state
	if saved_state == state: return True
	else: return False


@auth.route('/authorize')
def authorize():
	user = User.query.filter_by(name=current_user.name).first()
	if user.token: return redirect(url_for('main.profile'))
	state = str(uuid4())
	save_created_state(state)
	scope = ["identity", "modposts", "wikiedit", "wikiread"]
	return render_template('authorize.html', auth_link =auth_r.auth.url(scope, state, "permanent"))


@auth.route(AUTHORIZATION_PATH)
def authorized_callback():
	state = request.args.get('state', '')
	code = request.args.get('code', '')
	#Return a 403 error if state doesn't match
	if not is_valid_state(state):
		abort(403)
	refresh_token =auth_r.auth.authorize(code)
	User.query.filter_by(name=current_user.name).update({User.token:refresh_token}, synchronize_session = False)
	db.session.commit()
	return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
	return render_template('signup.html')
	

@auth.route('/signup', methods=['POST'])
def signup_post():
	name = request.form.get('name')
	password = request.form.get('password')
	password_confirm = request.form.get('password_confirm')
	if password != password_confirm:
		flash('Passwords do not match')
		return redirect(url_for('auth.signup'))
	user = User.query.filter_by(name=name).first()
	if user:
		flash('User already exists')
		return redirect(url_for('auth.signup'))
	new_user = User(name=name, password=generate_password_hash(password, method='sha256'))
	db.session.add(new_user)
	db.session.commit()
	return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('main.index'))