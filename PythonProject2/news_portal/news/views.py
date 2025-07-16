from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Article
from .filters import ArticleFilter

def search_articles(request):
    article_filter = ArticleFilter(request.GET, queryset=Article.objects.all())
    return render(request, 'news/search.html', {'filter': article_filter})

def news_list(request):
    articles = Article.objects.all().order_by('-pub_date')
    paginator = Paginator(articles, 10)  # 10 статей на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news/news_list.html', {'page_obj': page_obj})