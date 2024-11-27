# news_api
# SOA - Service Oriented Architecture
# MSA - Micro Service Architecture
# Архитектурный стиль REST Representation State Transfer
# /news (GET) - все новости
# /news/2 (GET) -новость №2
# /news (POST) - создание новой новости
# /news/2 (PUT) -изменение новости №2
# /news/2 (DELETE) -удаление новости №2
# RESTful приложение

# http://127.0.0.1:5000/api/news

import flask
from flask import jsonify, make_response, request
from data import db_session
from data.news import News

blueprint=flask.Blueprint('news_api', __name__, template_folder='templates')

#получение всех новостей
@blueprint.route('/api/news', methods=['GET'])
def get_news():
    db_sess= db_session.create_session()
    news=db_sess.query(News).all()
    return jsonify(
        {
            'news': [item.to_dict(only=('title', 'content', 'user.name')) for item in news]
        }
    )

#добавление новой новости
@blueprint.route('/api/news', methods=['POST'])
def create_news():
    if not request.json:
        return make_response(jsonify({'error': 'Пустой запрос'}), 400)
    elif not all(key in request.json for key in ['title', 'content', 'user_id', 'is_private']):
        return make_response(jsonify({'error': 'Неполный запрос'}), 400)
    db_sess = db_session.create_session()
    news = News(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private']
    )
    db_sess.add(news)
    db_sess.commit()
    return jsonify({'id': news.id})

#чтение отдельной новости
@blueprint.route('/api/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if news:
        return jsonify(
            {
                'news':news.to_dict(only=('title', 'content', 'user_id', 'is_private'))
            }
        )
    return make_response(jsonify({'error': 'Новость не найдена'}), 404)

#удаление новости
@blueprint.route('/api/news/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).get(news_id)
    if not news:
       return make_response(jsonify({'error': 'Новость не найдена'}), 404)
    db_sess.delete(news)
    db_sess.commit()
    return jsonify({'success': f'Новость {news.id} удалена'})


