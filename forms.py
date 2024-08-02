#Create Flask-WTF forms for user input validation. Forms include registration, login, meeting creation, etc., with validation rules.

# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, FileField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateMeetingForm(FlaskForm):
    invitees = StringField('Invitees (comma-separated emails)', validators=[DataRequired()])
    submit = SubmitField('Create Meeting')

class JoinMeetingForm(FlaskForm):
    code = StringField('Meeting Code', validators=[DataRequired(), Length(min=9, max=9)])
    submit = SubmitField('Join Meeting')

class ResetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordTokenForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UploadMeetingNotesForm(FlaskForm):
    notes = FileField('Select Notes File', validators=[DataRequired()])
    submit = SubmitField('Upload Notes')
