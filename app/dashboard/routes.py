from flask import Blueprint, render_template, session, redirect, url_for
from app.database.user import User
from app.dashboard.matcher import find_study_matches

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    
    # Get study matches
    matches = find_study_matches(user_id)
    
    return render_template('dashboard.html', user=user, matches=matches)
