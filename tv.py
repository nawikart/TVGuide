from flask import Flask, flash, session, request, redirect, render_template
import db.data_layer as db
from db.entities import User
from pprint import pprint

# for show in db.get_shows('candra'):
#     pprint(show.name)

# print(db.get_movie_ids_liked(1))

pprint(db.get_movie(1).name)

# result = db.create_user('iwan', 'iwan@outpost.com', 'asdfghjkl', 'asdfghjkl')

# if type(result) == User:
#     print(result.name)
# else:
#     for err in result:
#         print(err)

# def setup_web_session(user):
#     session['user_id'] = user.id
#     session['name'] = user.name
#     return True

# result = db.login('nawi2@outpost.com', 'asdfghjkl')
# if type(result) == User:
#     print('SUCCESS')
#     # setup_web_session(result)
# else:
#     for err in result:
#         print(err)