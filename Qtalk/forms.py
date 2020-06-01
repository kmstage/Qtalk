from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری',
            validators=[DataRequired(), Length(min=4, max=20)])

    email = StringField('ایمیل',
            validators=[DataRequired(), Email()])

    password = PasswordField('کلمه عبور',
            validators=[DataRequired()])

    confirm_password = PasswordField('تکرار کلمه عبور',
            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('!ثبت نام')

class LoginForm(FlaskForm):
    username = StringField('نام کاربری',
            validators=[DataRequired(), Length(min=4, max=20)])

    password = PasswordField('کلمه عبور',
            validators=[DataRequired()])

    remember = BooleanField('مرا به خاطر بسپار')

    submit = SubmitField('ورود')
