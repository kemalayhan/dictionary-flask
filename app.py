import requests
import json
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, RegisterForm

app = Flask(__name__)

app.config['SECRET_KEY'] = "159357852"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dictproject.db'
db = SQLAlchemy(app)



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Bu sayfayı görüntülemek için lütfen giriş yapın.')
            return redirect(url_for('index'))

    return decorated_function


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    dictionary = db.relationship('Dictionary', backref='owner')


class Dictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    word = db.Column(db.String(50))
    definition = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


def search_word(word):
    BASE_ENDPOINT = "https://wordsapiv1.p.rapidapi.com/words/"
    headers = {
    # 'x-rapidapi-key': "",
    # 'x-rapidapi-host': ""
        }
    ENDPOINT = BASE_ENDPOINT + word + '/definitions'
    res_word = requests.get(ENDPOINT, headers=headers)
    return res_word


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        searched_word = request.form.get('search')
        if searched_word == '':
            flash('Öğrenmek istediğiniz kelimeyi yazınız.')
            return redirect(url_for('index'))
        result_json = search_word(searched_word)
        result = json.loads(result_json.text)
        word = result.get('word')
        definitions = result.get('definitions')
        word_definition = ''
        for definition in definitions:
            word_definition += definition.get('definition') + '--'
        return render_template('index.html', word=word, definitions=definitions, word_definition=word_definition)
    else:
        return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    if request.method == 'POST':
        word = request.form.get('word')
        if word == '':
            flash('Kelime aratmadınız.')
            return redirect(url_for('index'))
        definitions = request.form.get('definitions')
        user_email = session['user']
        user = User.query.filter_by(email=user_email).first()
        dict_obj = Dictionary(word=word, definition=definitions, owner=user)
        db.session.add(dict_obj)
        db.session.commit()
        flash('Başarılı şekilde kelime kaydettiniz.')
        return redirect(url_for('index'))
        # return render_template('result.html', word=word, definitions=definitions)
    return "<p>ekleme yapılmadı</p>"


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate and request.method == 'POST':

        pw1 = form.password.data
        pw2 = form.confirm.data
        if pw1 != pw2:
            flash('Parolalar eşleşmek zorunda')
            return redirect(url_for('register'))
        username = form.username.data
        email = form.email.data
        query = User.query.filter((User.email == email) | (User.username == username)).first()
        if query:
            flash('Username ve email zaten kayıtlı.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Başarılı şekilde kayıt oldun')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/profile/')
@login_required
def profile():
    user_email = session['user']
    user = User.query.filter_by(email=user_email).first()
    dicts = user.dictionary
    return render_template('profile.html', **locals())  


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate:
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Başarılı şekilde giriş yaptın')
                session['logged_in'] = True
                session['user'] = user.email
                return redirect(url_for('index'))
            else:
                flash('Username or Password Incorrect')
                return redirect(url_for('login'))

    return render_template('login.html', form = form)

@app.route('/logout/')
def logout():
    session.clear()
    flash('Çıkış yapıldı.')
    return redirect(url_for('index'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)

