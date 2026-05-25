from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


'''

User signup form

'''

class SignupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    first_name = StringField("Email", validators=[DataRequired()])
    surname = StringField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    confirm_password = StringField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")