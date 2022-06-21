from django import forms

from ..models import Student


class StudentForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=True, label='Xác minh mật khẩu')
    date_of_birth = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
                                    input_formats=['%Y-%m-%d']
                                    )

    class Meta:
        model = Student
        fields = ['id', 'name', 'password', 'confirm_password', 'date_of_birth',
                  'gender', 'class_year', 'major']
        widgets = {'password': forms.PasswordInput()}
        labels = {
            'password': 'Mật khẩu',
            'name': 'Họ và Tên',
            'date_of_birth': 'Ngày sinh',
            'gender': 'Giới tính',
            'class_year': 'Khóa học',
            'major': 'Ngành học',
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     self.fields['id'].widget.attrs.update({'class': 'special'})
    #     # instance = kwargs.get('instance', None)
    #     # if kwargs.get('initial', None):
    #     #     for item in kwargs['initial']:
    #     #         del item
    #     #
    #     # super().__init__(*args, **kwargs)
    #     # # {'id': '00', 'name': 'Pham tien dat', 'date_of_birth': '23/03/1998', 'gender': 'nam', 'class_year': 'QH-2018-I/CQ', 'major': 'cong nghe thong tin'}
    #     # if card_info:
    #     #     self.fields['id'].initial = card_info['id']
    #     #     self.fields['name'].initial = card_info['name']
    #     #     self.fields['date_of_birth'].initial = card_info['date_of_birth']
    #     #     self.fields['gender'].initial = card_info['gender']
    #     #     self.fields['class_year'].initial = card_info['class_year']
    #     #     self.fields['major'].initial = card_info['major']
    #     #     # print(card_info)
    #     #     # if 'password' in card_info:
    #     #     #     self.fields['password'].initial = card_info['password']
    #     #     # if 'confirm_password' in card_info:
    #     #     #     self.fields['confirm_password'].initial = card_info['confirm_password']
    #
    #     print('init executed')

    def clean(self):
        cleaned_data = super(StudentForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Xác minh mật khẩu không trùng khớp."
            )
