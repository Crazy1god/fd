from django.contrib import messages
from django.contrib.auth import  login, logout, get_user_model
from django.contrib.auth.hashers import make_password
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View
import logging
from .forms import (
    RegisterForm, LoginForm, VerifyCodeForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .models import EmailCode

logger = logging.getLogger("django")
User = get_user_model()


class RegisterView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "register.html", {"form": RegisterForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = RegisterForm(request.POST)
        if not form.is_valid():
            return render(request, "register.html", {"form": form}, status=400)
        email = form.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            messages.error(request, "Пользователь с таким email уже существует.")
            return render(request, "register.html", {"form": form}, status=400)
        user = User.objects.create(
            email=email,
            password=make_password(form.cleaned_data["password1"]),
            is_active=False,
        )
        create_and_send_code(user, EmailCode.Purpose.REGISTRATION, "emails/verification_code.txt",
                             "Код подтверждения регистрации")
        messages.success(request, "Мы отправили код подтверждения на ваш email.")
        logger.info("User %s registered (pending verification)", email)
        return redirect("accounts:verify")


class VerifyEmailView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "verify.html", {"form": VerifyCodeForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = VerifyCodeForm(request.POST)
        if not form.is_valid():
            return render(request, "verify.html", {"form": form}, status=400)
        email = form.cleaned_data["email"].lower()
        code = form.cleaned_data["code"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
            return render(request, "verify.html", {"form": form}, status=404)
        ec = EmailCode.objects.filter(user=user, purpose=EmailCode.Purpose.REGISTRATION, code=code,
                                      used_at__isnull=True).order_by("-created_at").first()
        if not ec or ec.is_expired:
            messages.error(request, "Код недействителен или истек.")
            return render(request, "verify.html", {"form": form}, status=400)
        ec.mark_used()
        user.is_active = True
        user.save(update_fields=["is_active"])
        send_welcome(user)
        messages.success(request, "Email подтвержден. Можете войти.")
        logger.info("User %s verified email", email)
        return redirect("accounts:login")


class LoginView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "login.html", {"form": LoginForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm(request.POST)
        if not form.is_valid():
            # Логируем в security, если попытка входа неуспешна
            log_suspicious("Failed login attempt", ip=request.META.get("REMOTE_ADDR"))
            return render(request, "login.html", {"form": form}, status=400)
        user = form.cleaned_data["user"]
        if not user.is_active:
            messages.error(request, "Аккаунт не подтвержден.")
            return render(request, "login.html", {"form": form}, status=403)
        login(request, user)
        messages.success(request, "Вы вошли в систему.")
        logger.info("User %s logged in", user.email)
        return redirect("/")


class LogoutView(View):

    def post(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            email = request.user.email
            logout(request)
            logger.info("User %s logged out", email)
            return redirect("accounts:login")


class PasswordResetRequestView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "password_reset_request.html", {"form": PasswordResetRequestForm()})


def post(self, request: HttpRequest) -> HttpResponse:
    form = PasswordResetRequestForm(request.POST)
    if not form.is_valid():
        return render(request, "password_reset_request.html", {"form": form}, status=400)
    email = form.cleaned_data["email"].lower()
    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        # Не раскрываем, существует ли аккаунт
        logger.warning("Password reset requested for non-existing or inactive email: %s", email)
        messages.success(request, "Если такой email существует, мы отправили код.")
        return redirect("accounts:password_reset_confirm")
    create_and_send_code(user, EmailCode.Purpose.PASSWORD_RESET, "emails/password_reset_code.txt",
                         "Код для сброса пароля")
    messages.success(request, "Мы отправили код для сброса пароля на ваш email.")
    return redirect("accounts:password_reset_confirm")


class PasswordResetConfirmView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "password_reset_confirm.html", {"form": PasswordResetConfirmForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = PasswordResetConfirmForm(request.POST)
        if not form.is_valid():
            return render(request, "password_reset_confirm.html", {"form": form}, status=400)

        email = form.cleaned_data["email"].lower()
        code = form.cleaned_data["code"]
        new_password = form.cleaned_data["new_password"]
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
            return render(request, "password_reset_confirm.html", {"form": form}, status=404)

        ec = EmailCode.objects.filter(user=user, purpose=EmailCode.Purpose.PASSWORD_RESET, code=code,
                                      used_at__isnull=True).order_by("-created_at").first()
        if not ec or ec.is_expired:
            messages.error(request, "Код недействителен или истек.")
            return render(request, "password_reset_confirm.html", {"form": form}, status=400)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        ec.mark_used()
        notify_password_changed(user)
        messages.success(request, "Пароль успешно изменен.")
        logger.info("User %s changed password via reset", user.email)
        return redirect("accounts:login")