from secrets import token_hex
from os.path import splitext, join
from flask import render_template, url_for, flash, redirect, request
from Qtalk import app, db, bcrypt
from Qtalk.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from Qtalk.models import Post, User
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image


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

def save_picture(form_picture):
    random_hex = token_hex(8)
    _, f_ext = splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.email = form.email.data
        current_user.status = form.status.data
        db.session.commit()
        flash("اطلاعات شما با موفقیت بروزرسانی شد","success")
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.status.data = current_user.status

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='حساب کاربری',
                            image_file=image_file, form=form)

@app.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        flash('پست شما ایجاد شد', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='ارسال جدید', form=form)
