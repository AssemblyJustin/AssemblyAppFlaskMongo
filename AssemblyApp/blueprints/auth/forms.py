from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app import mongo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(), EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = mongo.db.users.find_one({'username': username.data})
        if user:
            raise ValidationError('Username is already in use.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')