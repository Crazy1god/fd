from django_filters import FilterSet, CharFilter, DateFilter
from django.forms import DateInput
from .models import Article
from django_filters.views import FilterView




class ArticleFilter(FilterSet):
    title = CharFilter(lookup_expr='icontains')
    author = CharFilter(field_name='author__username', lookup_expr='icontains')
    pub_date = DateFilter(field_name='pub_date', widget=DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Article
        fields = ['title', 'author', 'pub_date']


class ArticleFilterView(FilterView):
    queryset = Article.objects.all()
    filterset_class = ArticleFilter
    template_name = 'article_search.html'
    paginate_by = 10