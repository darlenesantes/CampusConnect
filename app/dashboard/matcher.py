<<<<<<< HEAD
# This is where we define matching logic for study groups
=======
from app.database.user import User
from app.database.course import Course, UserCourse

def find_study_matches(user_id):
    """Find study matches for a user based on shared courses and study style"""
    current_user = User.query.get(user_id)
    if not current_user:
        return []
    
    # Get user's courses
    user_courses = [uc.course_id for uc in current_user.courses]
    
    # Find other users with overlapping courses and same study style
    matches = []
    potential_matches = User.query.filter(
        User.id != user_id,
        User.study_style == current_user.study_style
    ).all()
    
    for match in potential_matches:
        match_courses = [uc.course_id for uc in match.courses]
        common_courses = set(user_courses) & set(match_courses)
        
        if common_courses:
            # Get course names
            course_names = [Course.query.get(course_id).name for course_id in common_courses]
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': len(common_courses) / len(user_courses) * 100
            })
    
    # Sort by compatibility
    matches.sort(key=lambda x: x['compatibility'], reverse=True)
    return matches[:10]  # Return top 10 matches
>>>>>>> e86c179ae670f259e3f9485453cc6bd9771385c7
