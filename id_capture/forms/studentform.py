from django import forms
from flatpickr import DatePickerInput

from ..models import Student


class StudentForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Xác minh mật khẩu')

    class Meta:
        model = Student
        fields = ['id', 'name', 'password', 'confirm_password', 'date_of_birth',
                  'gender', 'class_year', 'major']
        widgets = {
            'date_of_birth': DatePickerInput(),
            'password': forms.PasswordInput(),
        }
        labels = {
            'password': 'Mật khẩu',
            'name': 'Họ và Tên',
            'date_of_birth': 'Ngày sinh',
            'gender': 'Giới tính',
            'class_year': 'Khóa học',
            'major': 'Ngành học',
        }

    def clean(self):
        cleaned_data = super(StudentForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Xác minh mật khẩu không trùng khớp."
            )
