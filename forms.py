from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class UserSignUpForm(FlaskForm):
    """Form for adding a new user."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])
    first_name = StringField('First-Name', validators=[DataRequired()])
    last_name = StringField('Last-Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
class UserSignInForm(FlaskForm):
    """Form for signing in a user."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])

class EditUserForm(FlaskForm):
    """Form for editting user details."""

    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First-Name', validators=[DataRequired()])
    last_name = StringField('Last-Name', validators=[DataRequired()])
    mobile = StringField('(Optional) (XXX)-XXX-XXXX)', validators=[Length(min=10)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])

class LoginForm(FlaskForm):
    """Form for logging in user."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])