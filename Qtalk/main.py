from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)
app.config['SECRET_KEY'] = '50bec9ca1cabe7bee53088c068b7524f'

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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('اکانت شما با موفقیت ساخته شد', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='ثبت نام', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == "kaveh":
            username = "kaveh"
            flash(f' {username} خوش آمدید', 'success')
            return redirect(url_for('home'))
        else:
            flash('نام کاربری یا کلمه عبور اشتباه است', 'danger')

    return render_template('login.html', title='ورود', form=form)

if __name__ == "__main__" :
    app.run('0.0.0.0', 5000, debug=True)
