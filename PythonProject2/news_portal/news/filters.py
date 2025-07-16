import django_filters
from django import forms
from .models import Article


class ArticleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Автор')

    # Измените импорт виджета DateInput
    pub_date = django_filters.DateFilter(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата публикации после'
    )

    class Meta:
        model = Article
        fields = ['title', 'author', 'pub_date']