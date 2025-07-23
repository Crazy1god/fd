# импортируем библиотеку для работы с путями urls
from django.urls import path
# импортируем наше представление
from .views import PostsList, PostDetail

urlpatterns = [
    # путь ко всем товарам (пустой)
    path('',
         # вызываем метод as_view для того, чтобы представить класс PostsList в виде view
         PostsList.as_view()),
    path('<int:pk>', PostDetail.as_view())
]