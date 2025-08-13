from django.urls import path
from .views import (
RegisterView, VerifyEmailView, LoginView, LogoutView,
PasswordResetRequestView, PasswordResetConfirmView
)

app_name = "accounts"

urlpatterns = [
path("register/", RegisterView.as_view(), name="register"),
path("verify/", VerifyEmailView.as_view(), name="verify"),
path("login/", LoginView.as_view(), name="login"),
path("logout/", LogoutView.as_view(), name="logout"),
path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]