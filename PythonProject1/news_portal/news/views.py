from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from .models import Post

class PostCreateView(PermissionRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']
    permission_required = 'news.add_post'
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    ...

class PostUpdateView(PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    permission_required = 'news.change_post'


@login_required
def become_author(request):
    authors, _ = Group.objects.get_or_create(name='authors')
    request.user.groups.add(authors)
    return redirect('/')