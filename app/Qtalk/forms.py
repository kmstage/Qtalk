from flask_wtf import FlaskForm
from flask import flash
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from Qtalk.models import User
from Qtalk import bcrypt

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

class UpdateAccountForm(FlaskForm):

    email = StringField('ایمیل',
            validators=[DataRequired(), Email()])

    picture = FileField('آواتار جدید',
            validators=[FileAllowed(['jpg', 'png'])])

    status = StringField('استاتوس',
            validators=[Length(min=0, max=200)])

    submit = SubmitField('بروزرسانی')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('ایمیل شما قبلا ثبت شده')

class PostForm(FlaskForm):
    content = TextAreaField('پست جدید', validators=[DataRequired()])
    submit = SubmitField('ارسال')

class CommentForm(FlaskForm):
    content = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('ارسال نظر')

class UpdateForm(FlaskForm):
    content = TextAreaField('پست جدید', validators=[DataRequired()])
    submit = SubmitField('ویرایش')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class DirectForm(FlaskForm):
    content = TextAreaField('ارسال پیام', validators=[DataRequired()])
    submit = SubmitField('ارسال')

class ChangePwdForm(FlaskForm):
    old_password = PasswordField('کلمه عبور قدیمی',
            validators=[DataRequired()])
    new_password = PasswordField('کلمه عبور جدید',
            validators=[DataRequired()])
    confirm_new_password = PasswordField('تکرار کلمه عبور جدید',
            validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('تغیر کلمه عبور')

    def validate_old_password(self, old_password):
        if not(bcrypt.check_password_hash(current_user.password,old_password.data)):
            flash('کلمه عبور قدیمی شما اشتباه است !!!', 'danger')
            raise ValidationError('کلمه عبور قدیمی شما اشتباه است !!!')

    def validate_new_password(self, new_password):
        if not(self.confirm_new_password.data == new_password.data):
            flash('کلمه عبور جدید مطابقت ندارد !!!', 'danger')
            raise ValidationError('کلمه عبور جدید مطابقت ندارد !!!')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('درخواست ایمیل بازیابی !')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            flash('حسابی با ایمیل شما وجود ندارد. ابتدا باید ثبت‌نام کنید !', 'danger')
            raise ValidationError('حسابی با ایمیل شما وجود ندارد. ابتدا باید ثبت‌نام کنید !')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('کلمه عبور جدید',
            validators=[DataRequired()])
    confirm_password = PasswordField('تکرار کلمه عبور جدید',
            validators=[DataRequired()])
    submit = SubmitField('تغیر کلمه عبور')

    def validate_password(self, password):
        if not(self.confirm_password.data == password.data):
            flash('کلمه عبور جدید مطابقت ندارد !!!', 'danger')
            raise ValidationError('کلمه عبور جدید مطابقت ندارد !!!')
