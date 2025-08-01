from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import ArticleForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django_filters.views import FilterView
from .models import Article, Category, Subscription
from .filters import ArticleFilter

@login_required
def subscribe_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    Subscription.objects.get_or_create(user=request.user, category=category)
    # Можно добавить сообщение об успехе
    return redirect('category_detail', pk=category_id)

class NewsCreate(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news/article_form.html'
    success_url = '/news/'

    def form_valid(self, form):
        article = form.save(commit=False)
        article.type = 'news'  # Устанавливаем тип
        return super().form_valid(form)

class NewsUpdate(UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'news_form.html'

class NewsDelete(DeleteView):
    model = Article
    template_name = 'news_confirm_delete.html'
    success_url = reverse_lazy('news_list')


class ArticleFilterView(FilterView):
    model = Article
    filterset_class = ArticleFilter
    template_name = 'news/article_detail.html'
    paginate_by = 10

def search_articles(request):
    news_queryset = Article.objects.filter(type='news')  # Фильтруем по типу статьи (новости)
    paginator = Paginator(news_queryset, 10)  # 10 новостей на странице

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search_results.html')

def news_list(request):
    news_queryset = Article.objects.filter(type='news')  # Фильтруем по типу статьи (новости)
    paginator = Paginator(news_queryset, 10)  # Создаем пагинатор

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'news/news_list.html', {'articles': articles})
