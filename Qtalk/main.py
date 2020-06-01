from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == "__main__" :
    app.run('0.0.0.0', 5000, debug=True)
