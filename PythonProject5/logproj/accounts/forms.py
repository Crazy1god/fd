from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(min_length=8, widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=8, widget=forms.PasswordInput)


def clean(self):
    cleaned = super().clean()
    if cleaned.get("password1") != cleaned.get("password2"):
        raise ValidationError("Пароли не совпадают.")
    return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        user = authenticate(email=cleaned.get("email"), password=cleaned.get("password"))
        if not user:
            raise ValidationError("Неверные учетные данные.")
        cleaned["user"] = user
        return cleaned


class VerifyCodeForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(min_length=6, max_length=6)


class PasswordResetRequestForm(forms.Form):


    email = forms.EmailField()


class PasswordResetConfirmForm(forms.Form):


    email = forms.EmailField()
code = forms.CharField(min_length=6, max_length=6)
new_password = forms.CharField(min_length=8, widget=forms.PasswordInput)
