import praw
from praw.util.token_manager import BaseTokenManager
from flask import Flask, request
app = Flask(__name__)
class customTokenManager(BaseTokenManager):
  token = ""
	def post_refresh_callback(self, authorizer): self.token = authorizer.refresh_token
	def pre_refresh_callback(self, authorizer): authorizer.refresh_token = self.token
	def set_initial_token(self, setToken): self.token = setToken
refresh_token_manager = customTokenManager()
@app.route('/')
def homepage():	return f'<a href={auth_r.auth.url(["identity"], "state", "permanent")}>Permanent authorization link</a>'
@app.route('/authorize_callback')
def authorize_callback():
	refresh_token_manager.set_initial_token(auth_r.auth.authorize(request.args.get('code')))
	return f"You have {r.user.me().link_karma} link karma."
auth_r = praw.Reddit(client_id='',client_secret='',redirect_uri='http://127.0.0.1:5000/authorize_callback',user_agent='minimal praw OAuth Webserver by u/')
r = praw.Reddit(client_id='',client_secret='',token_manager=refresh_token_manager,user_agent='minimal praw OAuth Webserver by u/')
app.run(debug=True, port=5000)
