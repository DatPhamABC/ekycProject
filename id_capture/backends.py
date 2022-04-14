from django.contrib.auth.backends import BaseBackend
from django.contrib import messages

from id_capture.models import Student


class StudentBackend(BaseBackend):
    def authenticate(self, request, id=None, password=None, **kwargs):
        if id and password is not None:
            try:
                user = Student.objects.get(id=id)
            except Student.DoesNotExist:
                messages.error(request=request, message='User does not exist')
                return None

            pwd_valid = user.check_password(password)
            if pwd_valid:
                return user
            messages.error(request=request, message='Wrong password.')
        return None

    def get_user(self, user_id):
        try:
            return Student.objects.get(id=user_id)
        except Student.DoesNotExist:
            return None
