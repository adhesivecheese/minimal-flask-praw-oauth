from uuid import uuid4
import praw
from flask import Flask, request, url_for, abort
from praw.util.token_manager import BaseTokenManager

app = Flask(__name__)

CLIENT_ID = '' # Add your Client ID here
CLIENT_SECRET = '' # Add your Client Secret here
USER_AGENT = 'minimal praw OAuth Webserver by u/' #fill in your username, or change to whatever you'd like
BASE_URL = 'http://127.0.0.1'
SERVER_PORT = "5000"
AUTHORIZATION_PATH = "authorize_callback"

#Generate the Redirect URI
if not AUTHORIZATION_PATH.startswith("/"): AUTHORIZATION_PATH = "/" + AUTHORIZATION_PATH
REDIRECT_URI = BASE_URL + ":" + SERVER_PORT + AUTHORIZATION_PATH

"""
This is a really hacky and bad use of a BaseTokenManager that
just stores a token as a variable as part of the class, and needs
the additional set_initial_token function. The aim here isn't to
demonstrate a system you should use, only a minimum viable example
that will work for a single user for the runtime of the script.
"""
class customTokenManager(BaseTokenManager):
	token = ""

	def post_refresh_callback(self, authorizer):
		self.token = authorizer.refresh_token

	def pre_refresh_callback(self, authorizer):
		if authorizer.refresh_token is None:
			authorizer.refresh_token = self.token

	def set_initial_token(self, setToken):
		self.token = setToken

"""
This is a more proper usage of a baseTokenManager; it assumes an
SQLAlchemy database with a table Users that has a column refresh_token,
which is beyond the scope of a minimum viable example. Note that 
getting the initial refresh token is handled by pre_refresh_callback,
instead of needing a seperate class method.
"""
"""
class customTokenManager(BaseTokenManager):
	def post_refresh_callback(self, authorizer):
		Users.query.filter_by(name=current_user.name).update({Users.refresh_token:authorizer.refresh_token}, synchronize_session = False)
		db.session.commit()

	def pre_refresh_callback(self, authorizer):
		if authorizer.refresh_token is None:
			user = Users.query.filter_by(name=current_user.name).first()
			authorizer.refresh_token = user.refresh_token
"""

refresh_token_manager = customTokenManager()

"""
Save and verify states, to prevent xsrf attacks
Proper storing is left as an exercise to the reader
"""
saved_state = ""
def save_created_state(state):
	global saved_state
	saved_state = state
def is_valid_state(state):
	global saved_state
	if saved_state == state: return True
	else: return False


@app.route('/')
def homepage():
	"""
	See available scopes at end of this file. Scopes are given in a list. As additional 
	example, asking for the identity and submit scopes would be done as follows:
	`scopes = ["identity", "submit"]`
	See the comment at the end of this file for available scopes
	"""
	scopes = ["identity"]
	
	#generating a random state to send with the auth request can help prevent xsrf attacks
	state = str(uuid4()) 
	save_created_state(state)

	#Temporary authorization. Does not come with a refresh token
	link_no_refresh = auth_r.auth.url(scopes, state, "temporary")
	#Permanent authorization. Comes with a refresh token
	link_refresh = auth_r.auth.url(scopes, state, "permanent")

	#Generate and display the two links
	http_link_no_refresh = f'<a href={link_no_refresh}>link</a>'
	http_link_refresh = f'<a href={link_refresh}>link</a>'
	text = f"Not refreshable authorization {http_link_no_refresh}</br></br>"
	text += f"Refreshable authorization {http_link_refresh}</br></br>"
	return text

"""
This is the function that generates the actual authorization. It must 
be EXACTLY the path portion of the URI set in your app's settings
"""
@app.route(AUTHORIZATION_PATH)
def authorize_callback():
	#Get state and code from the returned URL; blank strings if not included
	state = request.args.get('state', '')
	code = request.args.get('code', '')

	#Return a 403 error if state doesn't match
	if not is_valid_state(state):
		abort(403)

	# "code" is the auth token - here we use it to login, and generate a refresh token (if applicable)
	refresh_token = auth_r.auth.authorize(code)

	"""
	If we have a temporary authorization, the refresh code will be blank, and we need to continue
	using auth_r. Otherwise, we can switch to using r, which has a token manager
	"""
	if refresh_token == '':
		user = auth_r.user.me()
	else:
		#This line is only needed with our janky minimal example, normally the pre_refresh_callback sets this as needed
		refresh_token_manager.set_initial_token(refresh_token)
		user = r.user.me()
	variables_text = f"State={state}</br>code={code}</br>refresh_token={refresh_token}"
	text = f'You are {user.name} and have {user.link_karma} link karma.'
	view_authorized_page = f"<a href='{url_for('authorized')}'>View authorized page</a>"
	back_link = "<a href='/'>Try again</a>"
	return variables_text + '</br></br>' + text + '</br>' + view_authorized_page + '</br>' + back_link


@app.route('/authorized')
def authorized():
	# If using temporary authorization, you should continue using auth_r, instead of r
	user = r.user.me()
	text = f'You are {user.name} and have {user.link_karma} link karma.'
	return text

if __name__ == '__main__':
	#The praw reddit instance to login via oauth
	auth_r = praw.Reddit(client_id=CLIENT_ID,
									client_secret=CLIENT_SECRET,
									redirect_uri=REDIRECT_URI,
									user_agent='OAuth Webserver example by u/adhesivecheese')

	# The praw reddit instance used to auth via refresh token
	r = praw.Reddit(
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		token_manager=refresh_token_manager,
		user_agent=USER_AGENT)
	app.run(debug=True, port=SERVER_PORT)


"""
Available scopes (fetched from https://www.reddit.com/api/v1/scopes.json on 11 June 2021):
account						:Update preferences and related account information. Will not have access to your email or password.
creddits					:Spend my reddit gold creddits on giving gold to other users.
edit							:Edit and delete my comments and submissions.
flair							:Select my subreddit flair. Change link flair on my submissions.
history						:Access my voting history and comments or submissions I've saved or hidden.
identity					:Access my reddit username and signup date.
livemanage				:Manage settings and contributors of live threads I contribute to.
modconfig					:Manage the configuration, sidebar, and CSS of subreddits I moderate.
modcontributors		:Add/remove users to approved user lists and ban/unban or mute/unmute users from subreddits I moderate.
modflair					:Manage and assign flair in subreddits I moderate.
modlog						:Access the moderation log in subreddits I moderate.
modmail						:Access and manage modmail via mod.reddit.com.
modothers					:Invite or remove other moderators from subreddits I moderate.
modposts					:Approve, remove, mark nsfw, and distinguish content in subreddits I moderate.
modself						:Accept invitations to moderate a subreddit. Remove myself as a moderator or contributor of subreddits I moderate or contribute to.
modtraffic				:Access traffic stats in subreddits I moderate.
modwiki						:Change editors and visibility of wiki pages in subreddits I moderate.
mysubreddits			:Access the list of subreddits I moderate, contribute to, and subscribe to.
privatemessages		:Access my inbox and send private messages to other users.
read							:Access posts and comments through my account.
report						:Report content for rules violations. Hide & show individual submissions.
save							:Save and unsave comments and submissions.
structuredstyles	:Edit structured styles for a subreddit I moderate.
submit						:Submit links and comments from my account.
subscribe					:Manage my subreddit subscriptions. Manage "friends" - users whose content I follow.
vote							Submit and change my votes on comments and submissions.
wikiedit					:Edit wiki pages on my behalf
wikiread					:Read wiki pages through my account

additionally:
*								:Access all scopes
"""
