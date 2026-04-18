# Запуск Celery в терминале, чтоб видеть что происходит
# сelery -A config worker -l info

from conf.celery import app
from utils.mail import send_message


@app.task()
def delay_send_message():
    send_message()
    print('письмо отправлено')


