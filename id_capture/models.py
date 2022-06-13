import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


def get_id_card_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.id, ext)
    return os.path.join('images/id', filename)


def get_face_image_path(instance, filename):
    filename = "%s.%s" % (instance.student_id, 'png')
    return os.path.join('images/face', filename)


class IDCard(models.Model):
    id_card = models.ImageField(upload_to=get_id_card_path, null=False, blank=False)


class Student(AbstractBaseUser, models.Model):
    GENDER = [
        ("M", 'nam'),
        ("F", 'nu'),
    ]
    MAJOR = [
        ("công nghệ thông tin", "Công nghệ thông tin"),
        ("khoa học máy tính", "Khoa học máy tính"),
        ("máy tính và robot", "Máy tính và robot"),
        ("cơ kỹ thuật", "Cơ kỹ thuật"),
        ("công nghệ kỹ thuật xây dựng", "Công nghệ kỹ thuật xây dựng"),
        ("công nghệ Hàng không vũ trụ", "Công nghệ Hàng không vũ trụ"),
        ("kỹ thuật điều khiển và tự động hóa", "Kỹ thuật điều khiển và tự động hóa"),
        ("công nghệ nông nghiệp", "Công nghệ nông nghiệp"),
    ]
    id = models.CharField(max_length=8, primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=250, null=False, blank=False)
    password = models.CharField(max_length=250, null=False, blank=False)
    date_of_birth = models.DateField(null=False, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER, default=None, null=True)
    class_year = models.CharField(max_length=15, null=False, blank=False)
    major = models.CharField(max_length=50, choices=MAJOR, null=False, blank=False)
    id_image = models.OneToOneField(IDCard, on_delete=models.CASCADE)
    face_image = models.BooleanField(default=False, null=False, blank=False)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['id', 'name', 'password', 'date_of_birth', 'gender', 'class_year',
                       'major', 'id_image', 'face_image']

    def get_student_info(self):
        student_info = ''
        for key in self:
            if 'id_image' in key.name or 'gender' in key.name or 'password' in key.name:
                continue
            student_info = student_info + str(key.value()) + " "
        return student_info


class FaceImage(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    image = models.ImageField(upload_to=get_face_image_path, null=True, blank=True)
