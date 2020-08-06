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

    return render(request, 'group.html', {'page': page, 'paginator': paginator})


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
    # post_list = Post.objects.all()
    # paginator = Paginator(post_list, 10)  

    # page_number = request.GET.get('page') 
    # page = paginator.get_page(page_number) 
    # return render(
    #     request,
    #     'index.html',
    #     {'page': page, 'paginator': paginator}
    # )
 
def post_view(request, username, post_id):
    return HttpResponse(f"post_view {username}, {post_id}")

        # тут тело функции
        #return render(request, 'post.html', {})


def post_edit(request, username, post_id):
    return HttpResponse(f"post_edit {username}, {post_id}")
        # тут тело функции. Не забудьте проверить, 
        # что текущий пользователь — это автор записи.
        # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
        # который вы создали раньше (вы могли назвать шаблон иначе)
        #return render(request, 'post_new.html', {})