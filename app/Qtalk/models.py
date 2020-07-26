from Qtalk import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import and_

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    password = db.Column(db.String(60), nullable=False)
    is_super_user = db.Column(db.String(5), default='false')
    birthday = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(300), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.now)
    date_register = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_time_explore = db.Column(db.DateTime, default=datetime.now)
    last_time_home = db.Column(db.DateTime, default=datetime.now)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='sender', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')
    disliked = db.relationship(
        'PostDislike',
        foreign_keys='PostDislike.user_id',
        backref='user', lazy='dynamic')
    messages_sent = db.relationship('Direct',
                                        foreign_keys='Direct.sender_id',
                                        backref='direct_author', lazy='dynamic')
    messages_received = db.relationship('Direct',
                                        foreign_keys='Direct.recipient_id',
                                        backref='direct_recipient', lazy='dynamic')

    def __repr__(self):
        return f'User("{self.username}", "{self.email}", "{self.image_file}")'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.date_posted.desc())

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    def dislike_post(self, post):
        if not self.has_disliked_post(post):
            dislike = PostDislike(user_id=self.id, post_id=post.id)
            db.session.add(dislike)

    def undislike_post(self, post):
        if self.has_disliked_post(post):
            PostDislike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_disliked_post(self, post):
        return PostDislike.query.filter(
            PostDislike.user_id == self.id,
            PostDislike.post_id == post.id).count() > 0

    def new_direct(self):
        result = 0
        conv = Conversation.query.filter(
        (Conversation.sender_id==self.id) | (Conversation.recipient_id==self.id)).all()
        for i in conv:
            result = result + i.new_messages(self)
        return result

    def conversations(self):
        conv = Conversation.query.filter(
        (Conversation.sender_id==self.id) | (Conversation.recipient_id==self.id))
        return conv

    def check_conversation(self, user_id):
        conv = Conversation.query.filter(
        and_(Conversation.sender_id==self.id, Conversation.recipient_id==user_id)| \
        and_(Conversation.sender_id==user_id ,Conversation.recipient_id==self.id)).first()
        return conv

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    dislikes = db.relationship('PostDislike', backref='post', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __repr__(self):
        return f'User("{self.id}", "{self.date_posted}")'

class Direct(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'Direct -> "{self.content}" '

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    sender_id = db.Column(db.Integer)
    recipient_id = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_midified = db.Column(db.DateTime, default=datetime.now)
    sender_last_seen = db.Column(db.DateTime, default=datetime(1900, 1, 1))
    recipient_last_seen = db.Column(db.DateTime, default=datetime(1900, 1, 1))

    def __repr__(self):
        return f'{self.sender_id} and {self.recipient_id}'

    def sender(self):
        user = User.query.filter_by(id=self.sender_id).first()
        return user

    def recipient(self):
        user = User.query.filter_by(id=self.recipient_id).first()
        return user

    def messages_info(self):
        messages = Direct.query.filter(
        and_(Direct.sender_id==self.sender_id, Direct.recipient_id==self.recipient_id)| \
        and_(Direct.sender_id==self.recipient_id ,Direct.recipient_id==self.sender_id)).order_by(
        Direct.date_posted.desc())
        count = messages.count()
        last_pm = messages.first()
        last_pm_sender_id = last_pm.sender_id
        last_pm_sender = User.query.filter_by(id=last_pm_sender_id).first()
        last_pm_sender_username = last_pm_sender.username
        last_pm_sender_date = last_pm.date_posted

        result = {'count':count, 'lastPmSender':last_pm_sender_username,
                'lastPmTime':last_pm_sender_date}
        return result

    def new_messages(self, user):
        new_messages=0
        messages = Direct.query.filter(
        and_(Direct.sender_id==self.sender_id, Direct.recipient_id==self.recipient_id)| \
        and_(Direct.sender_id==self.recipient_id ,Direct.recipient_id==self.sender_id)).order_by(
        Direct.date_posted.desc()).all()
        if self.sender_id == user.id :
            last_seen = self.sender_last_seen or datetime(1900, 1, 1)
            for message in messages:
                if message.date_posted > last_seen:
                    new_messages +=1
                else:
                    break
        else:
            last_seen = self.recipient_last_seen or datetime(1900, 1, 1)
            for message in messages:
                if message.date_posted > last_seen:
                    new_messages +=1
                else:
                    break
        return new_messages

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f'User("{self.id}", "{self.content}")'

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class PostDislike(db.Model):
    __tablename__ = 'post_dislike'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
