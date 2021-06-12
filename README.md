# minimal-flask-praw-oauth
This repository contains three minimal(ish) examples for using Flask in combination with PRAW to perform an Oauth signin on Reddit. Before we dive in, it is *very important* that it's specified that I am by no means an expert with Flask, PRAW,  OAuth, or SQLAlchemy; the files offered present a way that I've found works through a tedious process trial and error - they may not be a **good** way to do any of this, but it's a way I've found that works. With that out of the way, let's dive in to what I've got to offer and how to run them:

### Requirements and First Steps
* Make sure you have python 3.6 or greater, and pip. You need at least python 3.6 because all the string formatting is done with f-Strings; if you're stuck on an older version of python3 you *should* be able to easily convert the strings to the `str.format()` format. Information on python string formatting may be found [here](https://realpython.com/python-f-strings/).
* Install requirements in requirements.txt. This can be done with `pip install -r requirements.txt`. You may wish to do this in a virtual environment.
* create an app on Reddit using [this link](https://www.reddit.com/prefs/apps). 
	* The name can be whatever you'd like.
	* "web app" should be selected from the radio buttons
	* description can be left blank, or include whatever you want
	* about url should be set to an about page on your site, or the repo you're pulling this from
	* redirect uri must be set to the *exact* URI your authorization callback link will be located at. For this tutorial, we'll assume you're running flask on your local machine, on port 5000, and that your authorization path is `authorize_callback`. As such, your redirect uri should be `http:127.0.0.1/authorize_callback`
* Once you've created your application, make note of the client id (the string of text immediately below "web app"; your client secret, which can be found listed as "secret" if you hit the edit button on your app, and your redirect uri, should you be using different values than the tutorial.

### example.py
This file is *loosely* based on the oauth example in the [example webserver section of the praw v3.6.2 documentation](https://praw.readthedocs.io/en/v3.6.2/pages/oauth.html#an-example-webserver).
##### To Run
Fill in your Client ID on [line 10](https://github.com/adhesivecheese/minimal-flask-praw-oauth/blob/main/example.py#L10), and your Client Secret on [line 11](https://github.com/adhesivecheese/minimal-flask-praw-oauth/blob/main/example.py#L11). If using a different redirect uri, fill those values in on lines 13-15. Once this is done, you may run the script in several ways
* `python3 example.py` 
* If "python" is set to python 3 on your system, you may instead run `python example.py`
* You may also set the script as executable (`chmod a+x example.py`) and run it as `./example.py`
##### To use
After it's running, navigate to http:127.0.0.1:5000 in your browser to begin the authorization process.

##### Important Notes
* I commit a couple rather grave sins for the sake of simplicity and demonstration in setting up the token manager and storing the saved state. These examples are addressed in the more fleshed out project version of the example. using FileTokenManager instead of BaseTokenManager would make more sense in this example; however, there's documentation in PRAW [for using FileTokenManager](https://praw.readthedocs.io/en/latest/tutorials/refresh_token.html#using-and-updating-refresh-tokens), and I couldn't find any good examples of BaseTokenManager, so a bad, hacky example usage is inserted here.
* This is the only version of the examples that also offers a temporary authorization option.

### golfing_example.py
While well-documented code can certainly help explain a subject, oftentimes I find myself trying to strip a thing down to the bare minimum to see what actually needs to be done to do a thing, and what's extra. This is that example. Comments have been stripped, the state is statically defined so there's no defense against xsrf attacks, variables that are just used once are stripped and tossed directly inside the calls they're needed for. This is a TERRIBLE way to authorize with OAuth, but it *will* authorize you.

This example is based on the concept of [Code Golf](https://en.wikipedia.org/wiki/Code_golf). While not the shortest possible version of a script that lets you authenticate with Reddit, it is a stripped down version of example.py aiming to present the minimum amount of code you need to perform an authorization while still being legible.
##### To Run
* Fill in the variables on lines 5-7. Make sure your REDIRECT_URI appears exactly as it does in your app
* if you changed the path, make sure the app.route is changed to match on [line 23](https://github.com/adhesivecheese/minimal-flask-praw-oauth/blob/aadfbb32e6eb3c1439b9852509be3c37d6720a7e/golfing_example.py#L23)
* Set your flask app variable to golfing_example.py while in the directory containing the file: `export FLASK_APP=golfing_example.py`
* Run the script with `flask run -p 5000`
* Navigate to http://127.0.0.1:5000 to begin the authorization process
##### Important Notes
I cannot stress this enough, **DO NOT** use this code in a production environment. It's terrible, and is only presented for educational purposes.

### project (folder)
As I mentioned earlier, I'm not an authority here, so I won't claim that this is the *right* way to do PRAW OAuth with Flask, but it seems to at least be a *viable* way to do it that doesn't have anything obviously terrible about it. 

This example offers a webserver with an sqlite3 backend, allowing user signup and saved authorization for multiple users. As refresh tokens aren't saved in code in this example, it can actually be used by multiple users at once! It uses [Bulma](https://Bulma.io) for styling, but if you do webdev you should easily be able to port it to Bootstrap or whatever other CSS framework you'd like.

##### Setup
As this is a much more fleshed out example, slightly more setup is needed.
* Fill in the SECRET_KEY on [line 11 of \_\_init\_\_.py](https://github.com/adhesivecheese/minimal-flask-praw-oauth/blob/aadfbb32e6eb3c1439b9852509be3c37d6720a7e/project/__init__.py#L11). This is the key used to sign cookies; if this changes it'll invalidate your passwords.
* Set your desired scopes, as well as your Client ID, Client Secret, User Agent, and Redirect URI in `constants.py`. Available scopes will be found at the end of this Readme.
* run `python3 create_db.py` in the root directory to generate an empty database for use by the app.

##### To Run
* From the directory containing the project directory, run `export FLASK_APP=project`
* Run the script with `flask run -p 5000`
* Navigate to http://127.0.0.1:5000/signup to create an account; after account creation and login, you'll be directed to Reddit to authorize your account. Authorization will persist across signouts and script restarts. 

##### Important Notes
* If you look in project/main.py, you'll see a (maybe?) proper implementation of BaseTokenManager! It's definitely a *working* version of BaseTokenManager, in any case.

### Available scopes
(fetched from https://www.reddit.com/api/v1/scopes.json on 11 June 2021)

* **account** - Update preferences and related account information. Will not have access to your email or password.
* **creddits** - Spend my reddit gold creddits on giving gold to other users.
* **edit** - Edit and delete my comments and submissions.
* **flair** - Select my subreddit flair. Change link flair on my submissions.
* **history** - Access my voting history and comments or submissions I've saved or hidden.
* **identity** - Access my reddit username and signup date.
* **livemanage** - Manage settings and contributors of live threads I contribute to.
* **modconfig** - Manage the configuration, sidebar, and CSS of subreddits I moderate.
* **modcontributors** - Add/remove users to approved user lists and ban/unban or mute/unmute users from subreddits I moderate.
* **modflair** - Manage and assign flair in subreddits I moderate.
* **modlog** - Access the moderation log in subreddits I moderate.
* **modmail** - Access and manage modmail via mod.reddit.com.
* **modothers** - Invite or remove other moderators from subreddits I moderate.
* **modposts** - Approve, remove, mark nsfw, and distinguish content in subreddits I moderate.
* **modself** - Accept invitations to moderate a subreddit. Remove myself as a moderator or contributor of subreddits I moderate or contribute to.
* **modtraffic** - Access traffic stats in subreddits I moderate.
* **modwiki** - Change editors and visibility of wiki pages in subreddits I moderate.
* **mysubreddits** - Access the list of subreddits I moderate, contribute to, and subscribe to.
* **privatemessages** - Access my inbox and send private messages to other users.
* **read** - Access posts and comments through my account.
* **report** - Report content for rules violations. Hide & show individual submissions.
* **save** - Save and unsave comments and submissions.
* **structuredstyles** - Edit structured styles for a subreddit I moderate.
* **submit** - Submit links and comments from my account.
* **subscribe** - Manage my subreddit subscriptions. Manage "friends" - users whose content I follow.
* **vote** - Submit and change my votes on comments and submissions.
* **wikiedit** - Edit wiki pages on my behalf
* **wikiread** - Read wiki pages through my account

additionally:

* **\*** - Access all scopes
