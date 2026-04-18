# Запуск Celery в терминале, чтоб видеть что происходит
# сelery -A config worker -l info
import logging
from conf.celery import app
from utils.mail import send_message


logger = logging.getLogger('tasks')

@app.task()
def delay_send_message():
    send_message()
    logger.debug('письмо отправлено')


@app.task()
def delay_webhook_yookassa(pay_id, pay_status):
    logger.debug('Вебхук celery')
    logger.info('Статус заказа %s: %s ', pay_id, pay_status)

