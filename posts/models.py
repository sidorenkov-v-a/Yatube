from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        max_length=50
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст записи',
        help_text='Обязательное поле'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Не обязательное поле'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        limited_text = self.limited_text()
        return f'{self.author} | {limited_text}'

    def limited_text(self, max_len=100):
        if len(self.text) > max_len:
            return self.text[:max_len] + '...'
        else:
            return self.text

    limited_text.short_description = 'Описание'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        null=True

    )
    text = models.TextField(
        'Текст комментария',
    )
    created = models.DateTimeField(
        'Дата комментирования',
        auto_now_add=True
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
