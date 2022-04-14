from django import forms


class SigninForm(forms.Form):
    id = forms.CharField(required=True, label='ID',
                         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID number'}))
    password = forms.CharField(required=True, label='Mật khẩu',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""