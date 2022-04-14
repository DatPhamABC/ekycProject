from django.contrib import admin
from .models import Student
from .models import FaceImage

# Register your models here.
admin.site.register(Student)
admin.site.register(FaceImage)
