from django import forms
from flatpickr import DatePickerInput

from ..models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['id', 'name', 'date_of_birth', 'gender', 'class_year', 'major', 'id_image']
        widgets = {
            'date_of_birth': DatePickerInput(),
        }
        labels = {
            'name': 'Họ và Tên',
            'date_of_birth': 'Ngày sinh',
            'gender': 'Giới tính',
            'class_year': 'Khóa học',
            'major': 'Ngành học',
            'id_image': 'Ảnh thẻ sinh viên',
        }
