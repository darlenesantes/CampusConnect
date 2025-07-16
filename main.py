from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import secrets
import os
import git

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET_KEY')
REDIRECT_URI = "http://localhost:3000/oauth2callback"

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = secrets.token_hex(16)
CORS(app, origins=['http://localhost:3000'])
app.config['SECRET_KEY'] = secrets.token_hex(16)

@app.route("/")
def entry():
    return render_template("login.html")

@app.route("/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )
    return redirect(google_auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    code = request.args.get("code")

    token_res = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    })

    token_json = token_res.json()
    id_token = token_json.get("id_token")

    if not id_token:
        return jsonify({"error": "No ID token received", "response": token_json}), 400

    # Decode token to get user info (can also verify it)
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as grequests

    try:
        idinfo = google_id_token.verify_oauth2_token(id_token, grequests.Request(), CLIENT_ID)
        return jsonify({
            "email": idinfo["email"],
            "name": idinfo.get("name"),
            "sub": idinfo["sub"]
        })
    except Exception as e:
        return jsonify({"error": "Token verification failed", "details": str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="3000")