<<<<<<< HEAD
# This is where we do our forms like profilesetup and courses
=======
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email

class ProfileForm(FlaskForm):
    campus = SelectField('Campus', choices=[
        ('', 'Select Campus'),
        ('University of Illinois', 'University of Illinois'),
        ('Northwestern University', 'Northwestern University'),
        ('DePaul University', 'DePaul University')
    ], validators=[DataRequired()])
    
    major = StringField('Major', validators=[DataRequired()])
    year = SelectField('Year', choices=[
        ('', 'Select Year'),
        ('Freshman', 'Freshman'),
        ('Sophomore', 'Sophomore'),
        ('Junior', 'Junior'),
        ('Senior', 'Senior'),
        ('Graduate', 'Graduate')
    ], validators=[DataRequired()])
    
    study_style = SelectField('Study Style', choices=[
        ('', 'Select Style'),
        ('quiet', 'Quiet Study'),
        ('discussion', 'Discussion-Based'),
        ('group', 'Group Study')
    ], validators=[DataRequired()])
    
    preferred_location = StringField('Preferred Location')
    courses = SelectMultipleField('Courses', coerce=int)
    submit = SubmitField('Complete Profile')
>>>>>>> e86c179ae670f259e3f9485453cc6bd9771385c7
