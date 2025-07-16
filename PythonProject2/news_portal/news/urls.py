from django.urls import path
from .views import news_list, search_articles

urlpatterns = [
    path('', news_list, name='news_list'),
    path('search', search_articles, name='search_articles'),
]