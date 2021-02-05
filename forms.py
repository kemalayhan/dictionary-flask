from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

class RegisterForm(FlaskForm):
    username = StringField('enter your username', validators=[DataRequired()])
    email = StringField('enter your email', validators=[DataRequired()])
    password = PasswordField('your password', validators=[DataRequired()])
    confirm = PasswordField('enter your password again', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField('enter your username', validators=[DataRequired()])
    password = PasswordField('enter your password', validators=[DataRequired()])
