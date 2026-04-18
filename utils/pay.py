
import logging

from yookassa import Payment, Configuration
from conf import settings


Configuration.configure(account_id=settings.YOO_ID, secret_key=settings.YOO_SECRET_KEY)

logger = logging.getLogger('pay')


def pay_yookassa(order_id: int, total_price: int, return_url):
    """
    Создание платежа
    :param order_id: Номер заказа
    :param total_price: Общая сумма платежа
    :param return_url: Возврат после оплаты (страница профиля)
    :return:
    """
    order_name = f'Заказ № {order_id}_{total_price}'
    logger.info('Перехожу к оплате')
    try:
        payment = Payment.create(
            {
                'amount': {
                    'value': total_price,
                    'currency': 'RUB'
                },
                'confirmation': {
                    'type': 'redirect',
                    "return_url": return_url
                },
                'capture': True,  # Сразу списать деньги
                'description': order_name,
                'metadata': {
                    'order_id': order_id  # Чтобы в вебхуке понять, какой заказ оплачен
                },
            },
        )
        logger.info('Оплата заказа %s', order_name)

        # payment возвращается объект платежа с номером и статусом pending
        return payment
    except Exception as e:
        logger.warning('Ошибка при оплате заказа %s: %s', order_name, e)


