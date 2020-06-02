from flask import render_template, url_for, flash, redirect, request
from Qtalk import app, db, bcrypt
from Qtalk.forms import RegistrationForm, LoginForm
from Qtalk.models import Post, User
from flask_login import login_user, current_user, logout_user, login_required


posts = [
    {'username': 'Kaveh.m',
     'content' : 'سلام ... این اولین پست کیوتاک! هستش :))))',
     'date_posted': 'jun 1, 2020'
     },
     {'username': 'Kaveh.m',
     'content' : 'البته هنوز خیلی چیزا مونده ....',
     'date_posted': 'jun 2, 2020'
     }
]




@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pass)
        db.session.add(user)
        db.session.commit()
        flash('اکانت شما با موفقیت ساخته شد...حالا میتونید وارد بشید', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='ثبت نام', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f' {form.username.data} خوش آمدید', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است', 'danger')

    return render_template('login.html', title='ورود', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='حساب کاربری')
