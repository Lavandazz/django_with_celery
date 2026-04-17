from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView

from utils.tasks import delay_send_message



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
        """ Отправка письма """
        delay_send_message.delay()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'Home - Авторизация'
        return context

 