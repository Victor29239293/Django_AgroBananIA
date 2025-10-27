from django.shortcuts import render
from django.views import View



class AlertaComunitariaView(View):
    def get(self, request):
        return render(request, 'core/Dashboard/Modulo Alerta Comunitaria/alert_list.html')
