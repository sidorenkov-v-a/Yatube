from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import Paginator

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
    # group = get_object_or_404(Group, slug=slug)
    # posts = group.posts.all()[:12]
    # return render(request, 'group.html', {'group': group, 'posts': posts})
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
