from secrets import token_hex
from Qtalk.config import emails, usernames
from os.path import splitext, join
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from Qtalk import app, db, bcrypt, mail
from Qtalk.forms import (RegistrationForm, LoginForm,
                UpdateAccountForm, PostForm, UpdateForm, EmptyForm,
                CommentForm, DirectForm, ChangePwdForm, RequestResetForm,
                ResetPasswordForm)
from Qtalk.models import Post, User, Comment, Direct, Conversation
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
from datetime import datetime
from sqlalchemy import and_
from flask_mail import Message


def find_username(user_id):
    user = User.query.filter_by(id=user_id).first()
    result = user.username
    return result

def score_list(scores):
    result = []
    for i in scores :
        result.append(find_username(i.user_id))
    return result

def post_count(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).limit(5).all()
    count = 0
    today = datetime.now()
    today = today.strftime('%Y-%m-%d')
    for post in posts:
        if post.date_posted.strftime('%Y-%m-%d') == today:
            count +=1
    return count

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('درخواست بازیابی حساب کاربری',
                  sender='noreply@Qtalk.ir',
                  recipients=[user.email])
    msg.body = f'''برای بازیابی حساب خود از لینک زیر استفاده کنید:
                        {url_for('reset_token', token=token, _external=True)}
                        این پیام تا ۲ ساعت معتبر است.
                        اگر شما درخواست بازیابی حساب خودرا نفرستاده اید -> این پیام را نادیده بگیرید!
                        '''
    mail.send(msg)


@app.route('/')
def first_page():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    form2 = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f' {form.username.data} خوش آمدید', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است', 'danger')

    return render_template('first_page.html', form=form, form2=form2)

@app.route('/home')
@login_required
def home():
    last_time_home = current_user.last_time_home
    if  not last_time_home:
        last_time_home = datetime.now()
    current_user.last_time_home = datetime.now()
    db.session.commit()
    form = UpdateForm()
    postform = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=25)
    return render_template('home.html', posts=posts,
                                form=form, form2=postform, title="خانه",
                                last_time=last_time_home)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()

@app.route('/explore')
def explore():
    last_time_explore = current_user.last_time_explore
    if  not last_time_explore:
        last_time_explore = datetime.now()
    current_user.last_time_explore = datetime.now()
    db.session.commit()
    form = UpdateForm()
    postform = PostForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=25)
    return render_template('explore.html', posts=posts,
                                form=form, form2=postform, title="کاوش",
                                last_time=last_time_explore)

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
    form2 = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f' خوش آمدید {form.username.data}', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است', 'danger')

    return render_template('login.html', title='ورود', form=form, form2=form2)

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
    form2 = ChangePwdForm()
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
                            image_file=image_file, form=form, form2=form2, posts=posts)

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

@app.route("/new_comment/<int:post_id>", methods=['POST'])
@login_required
def new_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        content = form.content.data
        comment = Comment(content=form.content.data, post_id=post_id, sender=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('نظر شما ارسال شد.', 'success')
        return redirect(url_for('post', post_id=post_id))

@app.route("/delete_comment/<int:comment_id>", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.sender == current_user or comment.author.author == current_user :
        db.session.delete(comment)
        db.session.commit()
        return jsonify(status='ok', comment_id=comment.id)

    abort(403)


@app.route("/post/<int:post_id>")
def post(post_id):
    form = UpdateForm()
    form2 = CommentForm()
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.author.username, post=post, form=form, form2=form2)

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
    if post.comments:
        for comment in post.comments:
            db.session.delete(comment)

    db.session.delete(post)
    db.session.commit()
    flash('پست شما حذف شد', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user(username):
    form = EmptyForm()
    form2 = UpdateForm()
    direct_form = DirectForm()
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
    .order_by(Post.date_posted.desc())\
    .paginate(page=page, per_page=25)
    user_followers = user.followers.all()
    user_followings = user.followed.all()
    return render_template('user_post.html', posts=posts,
                user=user, form=form,
                form2=form2, filename='/static/profile_pics/' + user.image_file,
                user_followers=user_followers,user_followings=user_followings,
                direct_form=direct_form)

@app.route('/follow/<userid>', methods=['POST'])
@login_required
def follow(userid):
    user = User.query.filter_by(id=userid).first_or_404()
    current_user.follow(user)
    db.session.commit()
    follower = user.followers.count()
    following = user.followed.count()
    return jsonify(result="followed",
                   follower=follower,
                   following=following,
                   target=userid)

@app.route('/unfollow/<userid>', methods=['POST'])
@login_required
def unfollow(userid):
    user = User.query.filter_by(id=userid).first_or_404()
    current_user.unfollow(user)
    db.session.commit()
    follower = user.followers.count()
    following = user.followed.count()
    return jsonify(result="unfollowed",
                   follower=follower,
                   following=following,
                   target=userid)

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

@app.route("/post/<int:post_id>/scores", methods=['POST'])
def scores(post_id):
    post = Post.query.get_or_404(post_id)
    likes = score_list(post.likes.all())
    dislikes = score_list(post.dislikes.all())
    return jsonify(post_id = post_id,
                   likes = likes,
                   dislikes = dislikes)

@app.route("/delete_message/<int:message_id>", methods=['POST'])
@login_required
def delete_message(message_id):
    message = Direct.query.get_or_404(message_id)
    if message.direct_author == current_user :
        conv = current_user.check_conversation(message.recipient_id)
        if conv.messages_info()['count'] == 1:
            db.session.delete(message)
            db.session.delete(conv)
        db.session.commit()
        return jsonify(status='ok', message_id=message.id)

    abort(403)

@app.route("/send_message/<recipient>", methods=['POST'])
@login_required
def send_direct(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = DirectForm()
    conv = current_user.check_conversation(user.id)
    if conv :
        conv.date_midified = datetime.now()
    else:
        conv = Conversation(sender_id=current_user.id, recipient_id=user.id)
        db.session.add(conv)

    if conv.sender() == current_user:
        conv.sender_last_seen = datetime.now()
    else:
        conv.recipient_last_seen = datetime.now()

    if form.validate_on_submit():
        msg = Direct(direct_author=current_user, direct_recipient=user, content=form.content.data)
        db.session.add(msg)
        db.session.commit()
        flash('پیام ارسال شد','success')
        return redirect(url_for('conversation', username=recipient, unread=1))

@app.route('/messages')
@login_required
def messages():
    current_user.last_direct_read_time = datetime.now()
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.conversations().order_by(Conversation.date_midified.desc()).paginate(
                                                                                    page=page, per_page=25)

    return render_template('messages.html', messages=messages, title="پیام ها" )

@app.route('/conversation/<username>')
@login_required
def conversation(username):
    form = DirectForm()
    user = User.query.filter_by(username=username).first_or_404()
    conv = current_user.check_conversation(user.id)
    if conv :
        new_messages = conv.new_messages(current_user)
        messages = Direct.query.filter(
        and_(Direct.sender_id==current_user.id, Direct.recipient_id==user.id)| \
        and_(Direct.sender_id==user.id ,Direct.recipient_id==current_user.id)).order_by(
        Direct.date_posted)
        page_count = int(len(messages.all())/25) if len(messages.all())%25==0 else int(len(messages.all())/25) +1
        option = request.args.get('unread', 0, type=int )
        if option == 0 :
            page = request.args.get('page', 1, type=int)
        else:
            if len(messages.all())%25 < new_messages:
                page = request.args.get('page', page_count-1, type=int)
            else:
                page = request.args.get('page', page_count, type=int)
        messages=messages.paginate(page=page, per_page=25)

        if conv.sender() == current_user:
            last_seen = conv.sender_last_seen or datetime(1900, 1, 1)
            if page == page_count:
                conv.sender_last_seen = datetime.now()
                db.session.commit()
            else:
                if messages.items[-1].date_posted > last_seen:
                    conv.sender_last_seen = messages.items[-1].date_posted
                    db.session.commit()
        else:
            last_seen = conv.recipient_last_seen or datetime(1900, 1, 1)
            if page == page_count:
                conv.recipient_last_seen = datetime.now()
                db.session.commit()
            else:
                if messages.items[-1].date_posted > last_seen:
                    conv.recipient_last_seen = messages.items[-1].date_posted
                    db.session.commit()
        return render_template('conversation.html', messages=messages,
        form=form, title=user.username, last_seen=last_seen)
    return render_template('conversation.html', form=form, title=user.username)

@app.route('/change_pwd', methods=['POST'])
def change_pwd():
    form = ChangePwdForm()
    if form.validate_on_submit():
        new_hashed_pass = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        current_user.password = new_hashed_pass
        db.session.commit()
        logout_user()
        flash('میتونید با رمزجدید login کنید :) ', 'success')
        return redirect(url_for('login'))
    else:
        return redirect(url_for('account'))


@app.route("/reset_password", methods=['POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('ایمیل بازیابی حساب شما ارسال شده است !', 'info')
        return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('لینک بازیابی حساب شما معتبر نمیباشد !!!', 'warning')
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('میتوانید با پسورد جدید لاگین کنید !!!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='بازیابی کلمه عبور', form=form)
