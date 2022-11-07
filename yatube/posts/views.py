from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import pagination_pages

POSTS_PER_PAGE = 10


def index(request):
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    title = 'Последние обновления на сайте'
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
        'title': title
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    page_obj = pagination_pages(request, posts, POSTS_PER_PAGE)
    template = 'posts/profile.html'
    context = {
        'author': author,
        'count': count,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    count = author.posts.count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'count': count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', form.author)
    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    if author != request.user:
        return redirect('posts:post_detail', post.id)
    template = 'posts/create_post.html'
    is_edit = True
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': is_edit
    }
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.id)
    return render(request, template, context)
