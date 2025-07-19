from .views import news_list, search_articles
from django.urls import path
from .views import ArticleFilterView, NewsCreate, NewsDelete, NewsUpdate



urlpatterns = [
    path('news', news_list, name='news_list'),
    path('search/', ArticleFilterView.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', NewsUpdate.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', NewsDelete.as_view(), name='news_delete'),

]