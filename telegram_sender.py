import configparser
import requests

config= configparser.ConfigParser()
config.read('settings.ini')
token = config['Telegram']['bot_token']
id=config['Telegram']['chat_id']

def send_to_telegram(message):
    bot_token=token
    chat_id=id
    mess=f'Получено сообщение: {message}'
    requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={mess}')

if __name__== '__main__':
    send_to_telegram('Сообщение из main')
