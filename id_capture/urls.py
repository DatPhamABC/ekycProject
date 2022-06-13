from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login_student, name='login'),
    path('login/recognition-check', views.login_face_recognition_check, name='login_check'),
    path('login/face-recognition', views.login_student_recognition, name='student_face_recognition'),
    # path('home/student/<int:id>', views.login_student, name='student_home'),
    path('signup/instruction', views.instruction, name='instruction'),
    path('signup/id_card', views.card_register, name='id_card_register'),
    path('signup/info_register', views.register_form, name='info_register'),
    path('signup/facial_capture', views.facial_capture, name='facial_capture'),
    path('student', views.student, name='student'),
    path('logout', views.logout_student, name='logout')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
