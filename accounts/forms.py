from django import forms
from django.forms import DateInput
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser
from django.core.validators import RegexValidator
from captcha.fields import CaptchaField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from django.utils.translation import gettext_lazy as _

User = get_user_model()

nickname_validator = RegexValidator(
    regex=r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$',
    message='只能包含中文、英文、數字、底線 _ 和連字號 -'
)

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        label='使用者名稱',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': '請輸入使用者名稱'}),
    )
    nickname = forms.CharField(
        label='暱稱',
        max_length=30,
        required=False,
        validators=[nickname_validator],
        widget=forms.TextInput(attrs={'placeholder': '請輸入暱稱'}),
        help_text='只能包含中文、英文、數字'
    )

    captcha = CaptchaField()

    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'email', 'phone', 'birthday', 'password1', 'password2']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['captcha'].widget.attrs.update({'class': 'form-control'})

    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        if birthday:
            today = timezone.now().date()
            two_hundred_years_ago = today - timedelta(days=200 * 365)
            if birthday > today:
                raise ValidationError("生日不能是未來的日期")
            if birthday < two_hundred_years_ago:
                raise ValidationError("生日不能早於 200 年前")
        return birthday

class LoginForm(forms.Form):
    account = forms.CharField(
        label='帳號或 Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'account',
            'placeholder': '請輸入帳號或 Email'
        })
    )
    password = forms.CharField(
        label='密碼',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': '請輸入密碼'
        })
    )

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'birthday', 'phone']
        widgets = {
            'birthday': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nickname'].label = "暱稱"
        self.fields['birthday'].label = "生日"
        self.fields['phone'].label = "手機號碼"
