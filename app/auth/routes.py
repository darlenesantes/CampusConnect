# This is where we register auth, dashboards, and other routes
# Ex: /auth/login redirects to the login page (google oauth)
# ex: /callback handles token exchange and user creation (or something)
from flask_oauthlib.client import OAuth
from flask import Flask, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

google_client_id = 'your_google_client_id_here'
google_client_secret = 'your_google_client_secret_here'
google_redirect_uri = 'your_google_redirect_uri_here'

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=google_client_id,
    consumer_secret=google_client_secret,
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return jsonify({'data': me.data})
    return 'Hello! Log in with your Google account: <a href="/login">Log in</a>'

@app.route('/login')
def login():
    return google.authorize(callback=Flask.url_for('authorized', _external=True))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Login failed.'

    session['google_token'] = (response['access_token'], '')
    me = google.get('userinfo')
    # Here, 'me.data' contains user information.
    # You can perform registration process using this information if needed.

    return Flask.redirect(Flask.url_for('index'))

@app.route('/logout')
def logout():
    session.pop('google_token',p None)
    return Flask.redirect(Flask.url_for('index'))

@oauth.tokengetter
def get_google_oauth_token():
    return session.get('google_token')