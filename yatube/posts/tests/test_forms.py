from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            text='Тестовый текст, много текста',
            group=cls.group,
            author=cls.user,
        )

    def test_new_post_created(self):
        """при отправке валидной формы со страницы создания поста
        reverse('posts:create_post') создаётся новая запись в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'author': self.user,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        first_post = Post.objects.first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.user, first_post.author)
        self.assertEqual(self.post.group, first_post.group)

    def test_doing_post_edit(self):
        """при отправке валидной формы со страницы редактирования поста
        reverse('posts:post_edit', args=('post_id',))  происходит
        изменение поста с post_id в базе данных.."""
        form_data = {
            'text': self.post.text + 'Тестовый текст',
            'group': self.post.group.pk,
            'author': self.post.author,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )

        first_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.post.author, first_post.author)
        self.assertEqual(self.post.group, first_post.group)
