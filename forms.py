from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length

states = [
    ('AK', 'Alaska'),
    ('AL', 'Alabama'),
    ('AR', 'Arkansas'),
    ('AZ', 'Arizona'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DC', 'District of Columbia'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('IA', 'Iowa'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('MA', 'Massachusetts'),
    ('MD', 'Maryland'),
    ('ME', 'Maine'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MO', 'Missouri'),
    ('MS', 'Mississippi'),
    ('MT', 'Montana'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('NE', 'Nebraska'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NV', 'Nevada'),
    ('NY', 'New York'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VA', 'Virginia'),
    ('VT', 'Vermont'),
    ('WA', 'Washington'),
    ('WI', 'Wisconsin'),
    ('WV', 'West Virginia'),
    ('WY', 'Wyoming')
]

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

class ShippingAddressForm(FlaskForm):
    """Form for editting shipping or billing addresses."""

    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('(Optional) Address Line 2')
    state = SelectField('State', choices=states, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = StringField('XXXXX', validators=[Length(min=5)])

class BillingAddressForm(FlaskForm):
    """Form for editting shipping or billing addresses."""

    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('(Optional) Address Line 2')
    state = SelectField('State', choices=states, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = StringField('XXXXX', validators=[Length(min=5)])

class CartForm(FlaskForm):
    """Form for cart quantities."""

    quantity = IntegerField('Quantity', validators=[DataRequired()])
