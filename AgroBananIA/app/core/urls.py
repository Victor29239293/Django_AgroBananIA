from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.core.views import HomeView, DashboardView
from app.core.view.Modulo_deteccion_Enfermedades.Deteccion_enfermedad_view import DeteccionListView,analizar_imagen

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('deteccion/', DeteccionListView.as_view(), name='deteccion_list'),
    path('deteccion/analizar/', analizar_imagen, name='deteccion_analizar'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
