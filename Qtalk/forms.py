from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from Qtalk.models import User

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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('نام کاربری مورد نظر موجوده ... لطفا یه نام دیگه انتخاب کن')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('ایمیل شما قبلا ثبت شده ... اگه کلمه عبورتون رو فراموش کردین ... حسابتون رو بازیابی کنیدا')

class LoginForm(FlaskForm):
    username = StringField('نام کاربری',
            validators=[DataRequired(), Length(min=4, max=20)])

    password = PasswordField('کلمه عبور',
            validators=[DataRequired()])

    remember = BooleanField('مرا به خاطر بسپار')

    submit = SubmitField('ورود')
