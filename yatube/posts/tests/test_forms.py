from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from http import HTTPStatus


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
            'text': 'Тестовый текст, много текста',
            'group': self.group.pk,
            'author': self.user,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )

        Post.objects.filter(
            id=self.post.pk,
            text=self.post.text,
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertEqual(form_data['text'], self.post.text)
        self.assertEqual(self.user, self.post.author)
        self.assertEqual(self.post.group, self.post.group)

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
            data=form_data, follow=True,
        )

        first_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.post.author, first_post.author)
        self.assertEqual(self.post.group, first_post.group)

    def test_non_auth_user_new_post(self):
        # неавторизоанный не может создавать посты
        form_data = {
            'text': 'Тестовый текст, много текста',
            'group': self.group.pk,
            'author': self.user,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Тестовый текст').exists())
