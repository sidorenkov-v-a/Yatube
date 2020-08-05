from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            'group': 'Выберите группу',
            'text': 'Введите текст поста',
        }
        help_texts = {
            'group': 'Не обязательное поле',
            'text': 'Обязательное поле',
        }
