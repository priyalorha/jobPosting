from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed

from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, IntegerField, DateField
from wtforms.validators import DataRequired


class LoginSignUp(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Sign In/LoginIn')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    otp = StringField('Otp', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    mobile = StringField('Mobile', validators=[DataRequired()])
    otp = StringField('Otp', validators=[DataRequired()])
    submit = SubmitField('Sign Up')


class jobPostingForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    expiry_year = IntegerField('year', validators=[DataRequired()])
    expiry_month = IntegerField('month', validators=[DataRequired()])
    expiry_date = IntegerField('date', validators=[DataRequired()])
    submit = SubmitField('Submitß')


class jobSearch(FlaskForm):
    title = StringField('title')
    distance = StringField('distance')
    submit = SubmitField('Submit')


class EditProfileUser(FlaskForm):
    name = StringField('Name')
    email = StringField('Email')
    mobile = StringField('Mobile')
    submit = SubmitField('Submit')


