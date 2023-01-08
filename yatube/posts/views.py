from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Group, Post, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm

COUNT_OF_POSTS = 10
COP_MAIN_PAGE = 17


def index(request):
    post_list = Post.objects.all()
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядеть так:
    # post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.groups.all()
    paginator = Paginator(posts, COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    paginator = Paginator(posts, COUNT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count
    context = {
        'post': post,
        'posts_count': posts_count,
        'post_id': post_id,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id)
