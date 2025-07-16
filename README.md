# Campus Connect
A web app that matches college students with ideal study partners based on shared courses, study preferences, GPA, and more.

Built with **Python, Flask, SQLAlchemy, Google OAuth,** and **SQLite**.

Live at: https://seocampusconnect.pythonanywhere.com/

## Features
* Secure login via Google OAuth

* Profile setup: campus, major, GPA, study style, and enrolled courses

* Smart study group matching algorithm with compatibility scoring

* Campus-specific dining halls, study spots, and course data

* Demo mode with 50+ test students

* Personalized dashboard showing top study matches

## Log in with Google

* Fill out your profile

* View your top study partner matches on the dashboard

## Local Installation (for development)

1. Clone the repository
2. Create and activate a virtual environment (optional)

3. Install dependencies:

    ```pip install -r requirements.txt```

4. Set up environment variables by creating a .env file:

    ``` GOOGLE_CLIENT_ID=your_google_client_id ```
    ``` GOOGLE_CLIENT_SECRET=your_google_client_secret ```

5. Initialize the database with test data

6. Start the app

### How It Works
* **Google OAuth** logs in users and creates accounts if new.

* **Profile setup** collects user data and stores it in the database.

* **Matching logic** in find_study_matches() ranks study partners by shared courses, preferences, and major.

* **Dashboard** displays top matches and shared course info.

### Project Structure
```
campus-connect/
├── app/
│   ├── templates/              # HTML templates
│   ├── database/               # SQLAlchemy models
│   └── dummy_data/             # Seed data for campuses and users
├── main.py                     # App logic and routing
├── requirements.txt
├── .env                        # API credentials (not committed)
```
### Requirements
* Flask

* SQLAlchemy

* Authlib (for OAuth)

* python-dotenv

* Flask-CORS

Install with:

```pip install -r requirements.txt```
