import re
import json, requests
from flask import Flask, session, request, redirect, render_template, flash, url_for
from db.base import DbManager
from pprint import pprint
from db.entities import Movie, User, Like

EMAIL_REGEX = re.compile(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$')

db = DbManager()
ApiUrl = 'http://api.tvmaze.com'

def get_request(url):
    response = requests.get(url)
    return json.loads(response.text)

def get_all_likes_for(user_id):
    db = DbManager()
    return db.open().query(Like).filter(Like.user_id == user_id).all()

def get_show_ids_liked(user_id):
    show_ids = []
    db = DbManager()
    for s in db.open().query(Like).filter(Like.user_id == user_id).all():
        show_ids.append(s.show_id)
    return show_ids

def like(user_id, movie_id):
    like = Like()
    check = db.open().query(Like).filter(Like.user_id == user_id).filter(Like.movie_id == movie_id).all()
    if len(check) == 0:
        like.movie_id = movie_id
        like.user_id = user_id
        return db.save(like)

    return False

def unlike(user_id, movie_id):
    like = db.open().query(Like).filter(Like.movie_id == movie_id).filter(Like.user_id == user_id).one()
    like = db.delete(like)
    db.close()
    return like    

def get_movie_ids_liked(user_id):
    movie_ids = []
    for m in db.open().query(Like).filter(Like.user_id == user_id).all():
        movie_ids.append(m.movie_id)

    return movie_ids


def get_movie(movie_id):
    return db.open().query(Movie).filter(Movie.id == movie_id).one()

def get_shows(query):
    url = '{}/search/shows?q={}'.format(ApiUrl, query)
    shows = []
    for data in get_request(url):
        try:
            movie = db.open().query(Movie).filter(Movie.api_id == data['show']['id']).one()
        except:
            movie = Movie()
            movie.parse_json(data['show'])
            db.save(movie)

        shows.append(movie)

    return shows


def is_blank(name, field, error_msg):
    if len(field) == 0:
        error_msg.append('{} cant be blank'.format(name))
        return True
    return False
    
def create_user(name, email, password, confirm):

    is_valid = True
    error_msg = []

    is_valid = not is_blank('name', name, error_msg)
    is_valid = not is_blank('email', email, error_msg)
    is_valid = not is_blank('password', password, error_msg)
    is_valid = not is_blank('confirm', confirm, error_msg)

    if not EMAIL_REGEX.match(email):
        is_valid = False
        error_msg.append('invalid email format')

    if password != confirm:
        is_valid = False
        error_msg.append('password did not match')
    
    if(len(password) < 6):
        is_valid = False
        error_msg.append('password is too short')    

    if is_valid:
        try:
            user = User()
            user.name = name
            user.email = email
            user.password = password
            db.save(user)
            return user
        except:
            error_msg.append('email already registered.')


    return error_msg

def get_user_by_email(email):
    db = DbManager()
    return db.open().query(User).filter(User.email == email).one()    

def login(email, password):
    err_msg = []
    try:
        user = get_user_by_email(email)
        if user.password == password:
            return user
        else:
            err_msg.append('password do not match')
    except:
        err_msg.append('invalid login')

    return err_msg