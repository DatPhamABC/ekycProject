from django.contrib import admin
from .models import Student, IDCard, FaceImage

# Register your models here.
admin.site.register(Student)
admin.site.register(FaceImage)
admin.site.register(IDCard)
