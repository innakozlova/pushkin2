from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, TextAreaField, EmailField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import Email, DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name=StringField('Имя пользователя', validators=[DataRequired()])
    about=TextAreaField('Немного о себе')
    access = IntegerField('Access: ')
    submit = SubmitField('Отправить')
