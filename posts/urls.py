from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Просмотр постов группы
    path('group/<slug:slug>/', views.group_posts, name='group'),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    # Создание новой записи
    path('new_post/', views.new_post, name='new_post'),
    # Редактирование записи
    path(
        '<str:username>/<int:post_id>/edit/', 
        views.post_edit, 
        name='post_edit'
    ),
]
