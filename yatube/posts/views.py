from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:index')
    return render(
        request, 'processing_post.html',
        {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if (request.user.is_authenticated
        and Follow.objects.filter(user=request.user,
                                  author__username=username)):
        following = True
    posts = author.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'profile.html',
        {'author': author, 'page': page, 'following': following})


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    add_comment(request, username, post_id)
    return render(request, 'post.html', {'post': post, 'form': form})


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if post.author != request.user:
        return redirect(
            'posts:post',
            username=post.author.username,
            post_id=post_id)
    if form.is_valid():
        form.save()
        return redirect(
            'posts:post',
            username=post.author.username,
            post_id=post_id)
    return render(
        request, 'processing_post.html',
        {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    if request.method == 'POST':
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = get_object_or_404(Post, id=post_id)
            comment.save()
            return redirect(
                'posts:post',
                username=username,
                post_id=post_id)
    return redirect('posts:post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (not Follow.objects.filter(author=author, user=request.user)
            and request.user != author):
        Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_link = Follow.objects.filter(author=author, user=request.user)
    follow_link.delete()
    return redirect('posts:profile', username)
