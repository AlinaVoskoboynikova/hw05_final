from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  Создаю нового пользователя в БД
        cls.user = User.objects.create_user(username='TestUser')
        cls.user_2 = User.objects.create_user(username='TestUser_2')
        #  Создаю новую группу в БД
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )
        #  Создаю вторую группу в БД
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок_2',
            description='Тестовое описание_2',
            slug='test_slug_2'
        )
        #  Создаю новый пост в БД
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        #  Создаю второй пост в БД
        cls.post_2 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        #  Создаю третий пост в БД
        cls.post_3 = Post.objects.create(
            text='Тестовый текст',
            author=cls.user_2,
            group=cls.group
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_2
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}):
                    'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}):
                    'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def pages_show_correct_context(self, post):
        """Метод для проверки контекста на страницах"""
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.title, self.group.title)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.pages_show_correct_context(response.context['page_obj'][0])

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.pages_show_correct_context(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.pages_show_correct_context(response.context['page_obj'][0])

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.guest_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.context.get('post').pk, self.post.pk)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом
        при редактировании"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_not_in_uncorrect_group(self):
        """Проверка, что пост не попал в непредназначенную для него группу."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group_2.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        posts_object = response.context['posts']
        self.assertNotIn(self.post, posts_object)

    class PaginatorViewsTest(TestCase):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.user = User.objects.create_user(username='TestUser')
            cls.posts = []
            for i in range(13):
                post = Post.objects.create(
                    text='Тестовый текст',
                    author=cls.user,
                    group=cls.group
                )
                cls.posts.append(post)
            cls.group = Group.objects.create(
                title='Тестовый заголовок',
                slug='test_slug',
                description='Тестовое описание'
            )
            cls.guest_client = Client()
            cls.pages_uses_paginator = [
                reverse('posts:index'),
                reverse('posts:profile', kwargs={'username': cls.user}),
                reverse('posts:group_posts', kwargs={'slug': cls.group.slug}),
            ]

        def test_first_page_contains_ten_records(self):
            """Проверка, что на первой странице index,"""
            """profile и group_posts"""
            """отображаются 10 постов."""
            for reverse_page in self.pages_uses_paginator:
                with self.subTest(reverse_page=reverse_page):
                    response = self.client.get(reverse_page)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertEqual(len(
                        response.context['page_obj']), settings.NUM_POST)

        def test_second_page_contains_three_records(self):
            """Проверка, что на второй странице index,"""
            """profile и group_posts"""
            """отображаются 3 поста."""
            for reverse_page in self.pages_uses_paginator:
                with self.subTest(reverse_page=reverse_page):
                    response = self.client.get(reverse_page + '?page=2')
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                    self.assertEqual(len(
                        response.context['page_obj']),
                        settings.NUM_POST_IN_LAST_PAGE)

        def test_cache(self):
            """Проверка, что пост хранится в кэше."""
            response_index_1 = self.guest_client.get(reverse('posts:index'))
            self.assertContains(response_index_1, self.post_2)
            response_index_2 = self.guest_client.get(reverse('posts:index'))
            self.assertNotContains(response_index_2, self.post_2.text)
            cache.clear()
            response_index_3 = self.guest_client.get(reverse('posts:index'))
            self.assertContains(response_index_3, self.post_2.text)

        def test_new_post_appears_in_follow_index(self):
            """Новый пост появляется в ленте подписчиков."""
            follow_index_page = self.authorized_client.get(
                reverse('posts:follow_index'))
            self.assertIn(self.post_user.text, follow_index_page)

        def test_new_post_not_appears_in_follow_index(self):
            """Новый пост не появляется в ленте у"""
            """неподписанного пользователя."""
            follow_index_page = self.guest_client.get(
                reverse('posts:follow_index'))
            self.assertNotIn(self.post_3.text, follow_index_page)

        def test_login_user_can_subscribe(self):
            """Авторизованный пользователь может подписываться"""
            """на других юзеров."""
            response_get_profile = self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': self.user}))
            self.assertIn("Подписаться", response_get_profile)
            self.assertNotIn("Отписаться", response_get_profile)
            response_subscribe = self.authorized_client.post(
                reverse('posts:follow_index',
                        args=(self.user_2,)), follow=True)
            is_follow = Follow.objects.filter(
                user=self.user, author=self.user_2).count()
            self.assertEqual(is_follow, 1)
            self.assertIn("Отписаться", response_subscribe)

        def test_login_user_can_unsubscribe(self):
            """Авторизованный пользователь может отписываться от"""
            """других юзеров."""
            is_follow = Follow.objects.filter(
                user=self.user, author=self.user_2).count()
            self.assertEqual(is_follow, 1)
            response_unsubscribe = self.client_auth.post(
                reverse(
                    'posts:profile_unfollow',
                    args=(self.user_2,)), follow=True)
            self.assertIn("Подписаться", response_unsubscribe)
            follow_obj = Follow.objects.filter(
                user=self.user, author=self.user_2).count()
            self.assertEqual(follow_obj, 0)
