from flask import Flask, session, request, redirect, render_template, flash, url_for
import db.data_layer as db
from pprint import pprint
from db.entities import User


app = Flask(__name__)
app.secret_key = '0d599f0ec05c3bda8c3b8a68c32a1b47'

@app.route('/')
def index():
    if session:
        likes = db.get_all_likes_for(session['user_id'])
        movie_liked = []
        for l in likes:
            movie = db.get_movie(l.movie_id)
            pprint(movie.id)
            movie_liked.append(movie)
        return render_template('index.html', shows = movie_liked, movie_id_liked = db.get_movie_ids_liked(session['user_id']))
    else:
        return render_template('index.html')


@app.route('/search-redirect')
def search_redirect():
    return redirect(url_for('search', query=request.args['html_query']))

@app.route('/search/<query>')
def search(query):
    shows = db.get_shows(query)
    movie_id_liked = []
    if session:
        movie_id_liked = db.get_movie_ids_liked(session['user_id'])
    
    return render_template('index.html', shows = shows, movie_id_liked = movie_id_liked, destination = (request.url).replace('/', '||'))

@app.route('/unlike/<movie_id>/<destination>')
def unlike(movie_id, destination):
    db.unlike(session['user_id'], movie_id)

    if destination != '_':
        return redirect(destination.replace('||', '/'))
    else:
        return redirect(url_for('index'))

@app.route('/create-like/<movie_id>/<destination>')
def create_like(movie_id, destination):
    db.like(session['user_id'], movie_id)
    return redirect(destination.replace('||', '/'))

@app.route('/login-form')
def login_form():
    return render_template('login.html')

@app.route('/register-form')
def register_form():
    return render_template('register.html')

@app.route('/register-process', methods=['POST'])
def register_process():
    name = request.form['html_name']
    email = request.form['html_email']
    password = request.form['html_password']
    confirm = request.form['html_confirm']  

    result = db.create_user(name, email, password, confirm)  

    if type(result) == User:
        setup_web_session(result)
        return redirect(url_for('index'))        
    else:
        for err in result:
            flash(err)

    return redirect(url_for('register_form'))

@app.route('/login-process', methods=['POST'])
def login_process():
    email = request.form['html_email']
    password = request.form['html_password']

    result = db.login(email, password)
    if type(result) == User:
        setup_web_session(result)
        return redirect(url_for('index'))
    else:
        for err in result:
            flash(err)

    return redirect(url_for('login_form'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def setup_web_session(user):
    session['user_id'] = user.id
    session['name'] = user.name
    return True


app.run(debug=True)