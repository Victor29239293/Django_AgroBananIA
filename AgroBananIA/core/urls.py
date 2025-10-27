from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
