import logging

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.shortcuts import redirect

from utils.pay import pay_yookassa
from utils.tasks import delay_send_message

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
    """ Оплата через yookassa """
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

