import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import schedule
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')


def send_mail(email, subject, text):
    """
    Функция отправки сообщения
    :param email: адрес почты
    :param subject: тема
    :param text: текст письма
    :return: ничего не возвращает
    """

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    addr_from = os.getenv('FROM')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')
    port = os.getenv('PORT')

    # формируем сообщение
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = email
    msg['Subject'] = subject
    body = text
    msg.attach(MIMEText(body, 'plain'))

    # подкючаемся к серверу яндекса
    server = smtplib.SMTP_SSL(host, int(port))
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()
    return True

#if __name__ == '__main__':


    # message = """
    # Это проверка отправки почты
    # моим скриптом
    # """
    # send_mail('pochtovy@rambler.ru', 'проверка', message)
    #
    # mail_list =['pochtovy@rambler.ru', 'b@c.ru']
    # count=0 # глобальный счетчик писем
    #
    # def mail_task():
    #     global count
    #     send_mail('mail_list[count]', 'проверка', message)
    #     count+=1
    #
    # #while count<len(mail_list):
    # #    schedule.every(2).seconds.do(mail_task)
    # #    time.sleep(1)
    #
    # print('Рассылка завершена')
