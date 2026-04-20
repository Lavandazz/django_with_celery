"""
Для получения вебхуков от юкассы необзодимо настроить туннелирование.
Команда tuna http 8080 в терминале
"""


import logging
import json
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

from utils.pay import pay_yookassa
from utils.tasks import delay_send_message, delay_webhook_yookassa

logger = logging.getLogger('main')

# Create your views here.
class MainView(TemplateView):
    template_name = "layout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context
    

class MyLoginView(LoginView):
    template_name = "login.html"

    def form_valid(self, form):
        """ Отправка письма по клику Войти"""
        delay_send_message.delay()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Home - Авторизация'
        return context

 
class CreatePayView(View):
    """ Оплата через yookassa"""
    def get(self, request):
        order_id = 1
        price = 5050 
        return_url = request.build_absolute_uri(reverse('home'))
        payment = pay_yookassa(order_id=order_id,
                               total_price=price,
                               return_url=return_url)
         
        if payment:
            # Перенаправление на оплату в yookassa
            confirmation_url = payment.confirmation.confirmation_url

            messages.success(self.request, 'Заказ оформлен')
            logger.info('Оплата прошла успешно. Возвращаю на главную')
            return redirect(confirmation_url)
        
        else:
            logger.error('Ошибка в оптале или перенаправлении')


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """
    Проверка платежа
    В лк Юкасса необходимо указать полностью путь к вебхуку: домен/orders/payment/yookassa-webhook/
    """
    logger.info('Получение yookassa_webhook')
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # Извлекаем данные
    payment_id = data['object']['id']
    status = data['object']['status']

    logger.info('Получение yookassa_webhook payment_id - %s, status - %s', payment_id, status)
    
    delay_webhook_yookassa.delay(pay_id=payment_id, pay_status=status)
    return HttpResponse(status=200)
