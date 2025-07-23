"""NewsPortal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # чтобы адреса в будущем написанных нами страничек были доступны
    # нам для перехода по ним, добавим путь:
    path('pages/', include('django.contrib.flatpages.urls')),

    # чтобы все адреса из файла NewsPaper/urls.py
    # сами автоматически подключались когда мы их добавим.
    path('news/', include('NewsPaper.urls')),
]
