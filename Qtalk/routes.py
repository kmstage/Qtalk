from secrets import token_hex
from os.path import splitext, join
from flask import render_template, url_for, flash, redirect, request, abort
from Qtalk import app, db, bcrypt
from Qtalk.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, UpdateForm
from Qtalk.models import Post, User
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image


@app.route('/')
@app.route('/home')
def home():
    form = UpdateForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('home.html', posts=posts, form=form)

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

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('پست شما ایجاد شد', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='ارسال جدید', form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.author.username, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = UpdateForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        flash('پست شما ویرایش شد', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('update.html', title='ویرایش ارسال', form=form)


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('پست شما حذف شد', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
    .order_by(Post.date_posted.desc())\
    .paginate(page=page, per_page=25)
    return render_template('user_post.html', posts=posts, user=user)
