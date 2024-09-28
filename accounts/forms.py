from django import forms
from .models import Profile, MyUser
from django.forms.widgets import DateInput
import re



class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.is_strong_password(password):
            raise forms.ValidationError(
                'Password must be at least 8 characters long and contain letters, numbers, and special characters.'
            )
        return password

    def is_strong_password(self, password):
        return (len(password) >= 8 and
                re.search(r'\d', password) and
                re.search(r'[A-Za-z]', password) and
                re.search(r'[!@#$_%^&*(),.?":{}|<>]', password))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            raise forms.ValidationError("Пароли не совпадают.")

        return cleaned_data

    def clean_email(self):
        data = self.cleaned_data.get('email')
        if MyUser.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        data = self.cleaned_data.get('email')
        qs = MyUser.objects.exclude(id=self.instance.id).filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


class ProfileEditForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'] = forms.CharField(initial=user.first_name)
            self.fields['last_name'] = forms.CharField(initial=user.last_name)
            self.fields['email'] = forms.EmailField(initial=user.email)
