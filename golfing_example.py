import praw
from praw.util.token_manager import BaseTokenManager
from flask import Flask, request
app = Flask(__name__)
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = ''
USER_AGENT = 'minimal praw OAuth Webserver by u/'

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


auth_r = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri=REDIRECT_URI,user_agent=USER_AGENT)
r = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,token_manager=refresh_token_manager,user_agent=USER_AGENT)