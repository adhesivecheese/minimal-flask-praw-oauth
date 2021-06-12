from flask import Blueprint, render_template
from . import db
from flask_login import login_required, current_user
import praw
from praw.util.token_manager import BaseTokenManager
from .models import User
from constants import *

main = Blueprint('main', __name__)


class customTokenManager(BaseTokenManager):
	def post_refresh_callback(self, authorizer):
		User.query.filter_by(name=current_user.name).update({User.token:authorizer.refresh_token}, synchronize_session = False)
		db.session.commit()

	def pre_refresh_callback(self, authorizer):
		if authorizer.refresh_token is None:
			user = User.query.filter_by(name=current_user.name).first()
			authorizer.refresh_token = user.token


refresh_token_manager = customTokenManager()

r = praw.Reddit(
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		token_manager=refresh_token_manager,
		user_agent=USER_AGENT)


@main.route('/')
def index():
	return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
	return render_template('profile.html', name=current_user.name, karma=r.user.me().link_karma)