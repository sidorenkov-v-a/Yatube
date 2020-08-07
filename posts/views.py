from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .forms import PostForm
from .models import Group, Post

def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)  

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10) 

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    User = get_user_model()
    author = get_object_or_404(User, username=username)

    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)  

    page_number = request.GET.get('page') 
    page = paginator.get_page(page_number) 
    return render(request, 'profile.html', {'author': author, 'page': page, 'paginator': paginator})
 
def post_view(request, username, post_id):
    User = get_user_model()
    author = get_object_or_404(User, username=username)

    post = get_object_or_404(Post, author=author, id=post_id)

    return render(request, 'post.html', {'author': author, 'post': post})

def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect(f'/{username}/{post_id}')

    User = get_user_model()
    user = User.objects.get(username=username)
    post = Post.objects.get(author=user, id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            edited_post = form.save(commit=False)
            edited_post.author = post.author
            edited_post.id = post.id
            edited_post.pub_date = post.pub_date
            edited_post.save()
            return redirect(f'/{username}/{post_id}')
    else:
        form = PostForm(instance=post)

    return render(request, 'new_post.html', {'form': form})
