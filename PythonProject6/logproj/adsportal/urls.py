from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def index(_):
    return HttpResponse("OK")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("ads/", include("ads.urls")),
    path("", index),
]