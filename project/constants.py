scope = ["identity"]

CLIENT_ID = ''
CLIENT_SECRET = ''
USER_AGENT = 'minimal praw OAuth Webserver by u/adhesiveCheese'
BASE_URL = 'http://127.0.0.1'
SERVER_PORT = "5000"
AUTHORIZATION_PATH = "authorize_callback"

#Generate the Redirect URI
if not AUTHORIZATION_PATH.startswith("/"): AUTHORIZATION_PATH = "/" + AUTHORIZATION_PATH
REDIRECT_URI = BASE_URL + ":" + SERVER_PORT + AUTHORIZATION_PATH

