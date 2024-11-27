# Работаем на уровне ресурсов REST API v2 с использованием flask restful
# Пользователи
#Модули аутинтификации Flask -HTTPAuth
# Flask-jwt (создание и обращение через токен)

from flask import jsonify
from flask_restful import abort, Resource, reqparse

from data import db_session
from data.news import News
from data.sess_admin import Sess
from data.users import User


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, error=f'Пользователь {user_id} не найден')


def is_session_alive():
    db_sess=db_session.create_session()
    sess=db_sess.query(Sess).filter(Sess.title=='admin').first()
    if sess:
       if sess.content == 'super_long_admin_key':
          return True
    return False



#этот ресурс читает или удаляет отдельного пользователя
class UserResource(Resource):
    def get(self, user_id):
        if not is_session_alive():
            return jsonify({'error': 'Not allowed'})
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('id','name','about','email','level'))})

    def delete(self, user_id):
        if not is_session_alive():
            return jsonify({'error': 'Not allowed'})
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        news=session.query(User).filter(News.user_id==user_id).first()
        if news:
            return jsonify({'error': 'User has records'})
        session.delete(user)
        session.commit()
        return jsonify({'success': f'Пользователь удален'})



parser=reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('about', required=True)
parser.add_argument('email', required=True)
parser.add_argument('level', required=True, type=int)

class UsersResourceList(Resource):
    def get(self):
        if not is_session_alive():
            return jsonify({'error': 'Not allowed'})
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('id','name','about','email','level')) for item in users]})

    def post(self):
        if not is_session_alive():
            return jsonify({'error': 'Not allowed'})
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            about=args['about'],
            email=args['email'],
            level=args['level'])
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})
