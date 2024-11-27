import datetime
import configparser
import json, os
import requests
from flask import Flask, url_for, request, render_template, make_response, session, abort, jsonify
from flask import redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_login import current_user

from data.sess_admin import Sess
from mail_sender import send_mail
from forms.loginform import LoginForm
from forms.mailform import MailForm
from forms.user import RegisterForm
from forms.add_news import NewsForm
from werkzeug.utils import secure_filename

from data import db_session
from data.users import User
from data.news import News

from api_folder import news_api, our_resources, user_resources
from flask_restful import Api

from telegram_sender import send_to_telegram

MS1 = 'http://127.0.0.1:5000/api/news'

current_directory = os.path.dirname(__file__)
UPLOAD_FOLDER = f'{current_directory}/static/uploads'
ALLOWED_EXTENTIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'too_short_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

config = configparser.ConfigParser()  # объект для обращения к ini


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENTIONS


@app.errorhandler(400)
def http_400_handler(_):
    return make_response(jsonify({'error': 'Ошибка не найдена'}), 400)


@app.errorhandler(401)
def http_401_handler(error):
    return render_template('error401.html', title='Требуется аутентификация')


@app.errorhandler(404)
def http_404_handler(error):
    return make_response(jsonify({'error': 'Новость не найдена'}), 404)


@app.route('/')
@app.route('/index')
def index():
    param = {}
    param['text'] = 'Экскурсии в Царском селе'
    param['title'] = 'Главная'
    return render_template('index.html', **param)


@login_manager.user_loader
def user_loader(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/admin')
@login_required
def admin():
    return render_template('admin/index.html', title='Панель администрирования')


@app.route('/adminuser')
@login_required
def users():
    users = requests.get('http://127.0.0.1:5000/api/v2/users').json()
    # print(users)
    if users.get('error', None) or users.get('message', None):
        return redirect('/')
    return render_template('admin/users.html', title='Пользователи сайта', users=users['users'])


@app.route('/admin/user_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete(id):
    if not current_user.is_admin():
        return redirect('/')
    res = requests.delete(f'http://127.0.0.1:5000/api/v2/user/{id}').json()
    temp = res.get('error', None)
    if temp:
        return render_template('admin/users.html', title='temp')
    return redirect('/adminuser')


@app.route('/session_test')
def session_test():
    visit_count = session.get('visit_count', 0)
    session['visit_count'] = visit_count + 1
    # visit_count % 3 - 0,1,2  номер новости или контента в зависимости от visit count
    # session.pop('visit_count', None) # если надо программно уничтожить сессию
    return make_response(f'Вы посетили данную страницу {visit_count} раз')


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'GET':
        return render_template('weather.html', title='Погода', form=None)  # форма с городом
    elif request.method == 'POST':
        config.read('settings.ini')
        # return render_template('weather.html', title='Погода в городе', form=request.form) #обращение к API openweathermap
        city = request.form['city']
        if len(city) < 2:
            flash('Город введен не полностью')
            return redirect(request.url)
        key = config['Weather']['key']

        res = requests.get('http://api.openweathermap.org/data/2.5/find',
                           params={'q': city, 'type': 'like', 'units': 'metric', 'APPID': key})

        data = res.json()

        temp = data['list'][0]['main']
        params = {}
        params['temper'] = temp['temp']
        params['press'] = temp['pressure']
        params['humid'] = temp['humidity']

        return render_template('weather.html', title=f'Погода в {city}', form=request.form, params=params)


# тестируем наш API
@app.route('/apitest')
def api_test():
    res = requests.get(MS1).json()
    return render_template('apitest.html', title='Тестируем наш первый API', news=res['news'])


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message='Пароли не совпадают')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message=f'Пользователь с Email {form.email.data} уже зарегистрирован')
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if user.is_admin():
                sess_make = Sess(
                    title='admin',
                    content='super_long_admin_key'
                )
                db_sess.add(sess_make)
                db_sess.commit()
            return redirect('/')
        return render_template('login.html', title='Ошибка авторизации', message='Неправильная пара: логин-пароль!',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    db_sess = db_session.create_session()
    sess = db_sess.query(Sess).filter(Sess.title == 'admin').first()
    if sess:
        db_sess.delete(sess)
        db_sess.commit()
    return redirect('/')


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/blog')
    return render_template('add_news.html', title='Добавление отзыва', form=form)


@app.route('/blog/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()

        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            form.submit.data = 'Отредактировать'
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()

        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/blog')
        else:
            abort(404)
    return render_template('add_news.html', title='Редактирование отзыва', form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()

    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/blog')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html', title='Выбор файла', form=None)
    elif request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не был найден')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Файл не был отправлен')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Загрузка файлов данного типа запрещена')
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template('upload.html', title='Файл загружен', form=True)


@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    form = MailForm()
    params = {}
    if form.validate_on_submit():
        name = form.username.data
        params['name'] = name
        phone = form.phone.data
        params['phone'] = phone
        email = form.email.data
        params['email'] = email
        message = form.message.data
        params['message'] = message
        params['page'] = request.url

        text = f""" Пользователь {name} оставил Вам сообщение:
        {message}.
        Его телефон {phone},
        Email: {email},
       # Страница:{request.url}.
        """

        text_to_user = f""" 
        Уважаемая {name} !
                Ваши данные:
                Его телефон {phone},
                Email: {email},
                успешно по получены.
                Ваше сообщение: {message} принято к рассмотрению.
                Страница:{request.url}.
        """
        send_mail('pochtovy@rambler.ru', 'Запрос с сайта', text_to_user)
        send_mail('inkys@yandex.ru', 'Запрос с сайта', text)

        send_to_telegram(text)
        return render_template('mailresult.html', title='Ваши данные', params=params)

    return render_template('contacts.html', title='Наши контакты', form=form)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', title='О нас')


@app.route('/blog')
def blog():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template('blog.html', title='Отзывы', news=news)


if __name__ == '__main__':
    db_session.global_init('db/blogs.db')
    app.register_blueprint(news_api.blueprint)
    api.add_resource(our_resources.NewsResource, '/api/v2/news/<int:news_id>')
    api.add_resource(our_resources.NewsResourceList, '/api/v2/news')
    api.add_resource(user_resources.UserResource, '/api/v2/user/<int:user_id>')
    api.add_resource(user_resources.UsersResourceList, '/api/v2/users')
    app.run(port=5000, host='127.0.0.1')
