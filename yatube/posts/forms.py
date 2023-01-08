from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ("text", "group")
        labels = {
            "text": "Текст сообщения",
            "group": "Группа"
        }
