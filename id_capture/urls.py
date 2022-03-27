from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup/instruction', views.instruction, name='instruction'),
    path('signup/info_register', views.register_form, name='info_register'),
    path('signup/facial_capture', views.facial_capture, name='facial_capture')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
