import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': self.post.text,
            'author': self.user,
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                author=self.user,
                group=self.group,
                image=self.post.image,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        post_id = self.post.pk
        form_data = {
            'text': self.post.text,
            'author': self.user,
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}))
        self.assertEqual(self.post.pk, post_id)

    def test_create_post_unauthorized_user(self):
        """"Неавторизованный пользователь не может попасть"""
        """на страницу create,"""
        """"и его перенаправляет на страницу авторизации."""
        form_data = {
            'text': self.post.text,
            'author': self.user,
            'group': self.group.pk,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={new_post_url}')

    def test_post_output_with_picture(self):
        url_names = ['/',
                     f'/group/{self.group.slug}/',
                     f'/profile/{self.user}/',
                     f'/posts/{self.post.pk}/',
                     ]

        for url in url_names:
            with self.subTest(url=url):
                url_page = self.guest_client.get(url)
                self.assertIn("<img", url_page.content.decode())

    def test_log_user_comment_post(self):
        """Авторизованный пользователь может комментировать пост"""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    # Добавляю тестирование
    def test_unlogged_user_cant_comment_post(self):
        """Неавторизованный пользователь не может комментировать пост"""
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertRedirects(response,
                             reverse('users:login') + '?next=' + reverse(
                                 'posts:add_comment',
                                 kwargs={'post_id': self.post.pk}))
