from django.shortcuts import render

from django.views.generic import ListView, DetailView

from .models import Post


class PostsList(ListView):
    model = Post

    template_name = 'news.html'


    context_object_name = 'news'


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
