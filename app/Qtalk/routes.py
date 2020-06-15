from secrets import token_hex
from Qtalk.config import emails, usernames
from os.path import splitext, join
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from Qtalk import app, db, bcrypt
from Qtalk.forms import (RegistrationForm, LoginForm,
                UpdateAccountForm, PostForm, UpdateForm, EmptyForm)
from Qtalk.models import Post, User
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from datetime import datetime


def post_count(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).limit(5).all()
    count = 0
    today = datetime.now()
    today = today.strftime('%Y-%m-%d')
    for post in posts:
        if post.date_posted.strftime('%Y-%m-%d') == today:
            count +=1
    return 1


@app.route('/')
def first_page():
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

    return render_template('first_page.html', form=form)

@app.route('/home')
@login_required
def home():
    form = UpdateForm()
    postform = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=25)
    return render_template('home.html', posts=posts, form=form, form2=postform, title="خانه")

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@app.route('/explore')
def explore():
    form = UpdateForm()
    postform = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('explore.html', posts=posts, form=form, form2=postform, title="کاوش")

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
            flash(f' خوش آمدید {form.username.data}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است', 'danger')

    return render_template('login.html', title='ورود', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('first_page'))

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
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=current_user)\
    .order_by(Post.date_posted.desc())\
    .paginate(page=page, per_page=25)
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
                            image_file=image_file, form=form, posts=posts)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        if post_count(current_user.username) <= 3:
            content = form.content.data.encode('utf-8')
            post = Post(content=content, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('پست شما ایجاد شد', 'success')
            return redirect(url_for('home'))
        else:
            flash('امروز بیشتر از ۴ پست ارسال کردید', 'warning')
            return redirect(url_for('home'))
    return render_template('create_post.html', title='ارسال جدید', form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    form = UpdateForm()
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.author.username, post=post, form=form)

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
        return redirect(url_for('post',post_id=post.id))
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
def user(username):
    form = EmptyForm()
    form2 = UpdateForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
    .order_by(Post.date_posted.desc())\
    .paginate(page=page, per_page=25)
    return render_template('user_post.html', posts=posts,
                user=user, form=form,
                form2=form2, filename='/static/profile_pics/' + user.image_file)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('کاربر مورد نظر یافت نشد', 'warning')
            return redirect(url_for('explore'))
        if user == current_user:
            flash('خودتو ک نمیتونی فالو کنی :)', 'primary')
            return redirect(url_for('explore'))
        current_user.follow(user)
        db.session.commit()
        flash('شما {} را دنبال میکنید'.format(username), 'info')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('کاربر مورد نظر یافت نشد', 'warning')
            return redirect(url_for('explore'))
        if user == current_user:
            flash('خودتو ک نمیتونی آنفالو کنی :)', 'primary')
            return redirect(url_for('explore'))
        current_user.unfollow(user)
        db.session.commit()
        flash('کاربر {} دنبال نمیشود'.format(username), 'info')
        return redirect(url_for('user',username=username))
    else:
        return redirect(url_for('explore'))

@app.route('/like/<int:post_id>/<action>')
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
        likes = post.likes.count()
        dislikes = post.dislikes.count()
        result = f"{likes} لایک و {dislikes} دیسلایک"
        return jsonify(post_id = post_id,
                       state = 'like',
                       result = result)
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
        likes = post.likes.count()
        dislikes = post.dislikes.count()
        result = f"{likes} لایک و {dislikes} دیسلایک"
        return jsonify(post_id = post_id,
                       state = 'unlike',
                       result = result)

@app.route('/dislike/<int:post_id>/<action>')
@login_required
def dislike_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'dislike':
        current_user.dislike_post(post)
        db.session.commit()
        likes = post.likes.count()
        dislikes = post.dislikes.count()
        result = f"{likes} لایک و {dislikes} دیسلایک"
        return jsonify(post_id = post_id,
                       state = 'dislike',
                       result = result)
    if action == 'undislike':
        current_user.undislike_post(post)
        db.session.commit()
        likes = post.likes.count()
        dislikes = post.dislikes.count()
        result = f"{likes} لایک و {dislikes} دیسلایک"
        return jsonify(post_id = post_id,
                       state = 'undislike',
                       result = result)

@app.route('/adminzone')
@login_required
def adminzone():
    if current_user.email in emails and current_user.username in usernames:
        users = User.query.all()
        posts = Post.query.all()
        num_users = len(users)
        num_posts = len(posts)
        return render_template('admin.html', users=users, posts=posts, num_users=num_users, num_posts=num_posts)
    else:
        return redirect(url_for('home'))

@app.route('/users')
@login_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.date_register.desc()).paginate(page=page, per_page=50)
    return render_template('users.html', users=users, title="کاربران")

@app.route('/rules')
def rules():
    return render_template('rules.html',title="قوانین")

@app.errorhandler(403)
def forbiden(e):
    flash("لطفا وارد شوید.","info")
    return redirect(url_for('login'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',title='یافت نشد')