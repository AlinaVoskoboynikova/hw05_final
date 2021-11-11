from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #  Создаю новую группу в БД для тестирования /group/test_slug/
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test_slug',
            description='Тестовое описание'
        )

        #  Создаю новый пост в БД для тестирования /post/post_id/
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_access_to_address(self):
        """Проверка доступности адресов любому пользователю"""
        url_names = ['/',
                     '/about/author/',
                     '/about/tech/',
                     f'/group/{self.group.slug}/',
                     f'/profile/{self.user}/',
                     f'/posts/{self.post.pk}/',
                     ]
        for adress in url_names:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create(self):
        """Проверка доступности адреса /create/ авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_id_edit(self):
        """Проверка доступности адреса /posts/post_id/edit/ автору поста"""
        response = self.authorized_client.get(f'/posts/'
                                              f'{self.post.pk}/'
                                              f'edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # Добавляю тестирование новых urls
    def test_comment(self):
        """Проверка доступности адреса /posts/post_id/comment"""
        """авторизованному пользователю"""
        response = self.authorized_client.get(f'/posts/'
                                              f'{self.post.pk}/'
                                              f'comment')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_index(self):
        """Проверка доступности адреса /follow/"""
        """авторизованному пользователю"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_follow(self):
        """Проверка доступности адреса /profile/username/follow/"""
        """авторизованному пользователю"""
        response = self.authorized_client.get(f'/profile/'
                                              f'{self.user}/'
                                              f'follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_unfollow(self):
        """Проверка доступности адреса /profile/username/unfollow/"""
        """авторизованному пользователю"""
        response = self.authorized_client.get(f'/profile/'
                                              f'{self.user}/'
                                              f'unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page(self):
        """Проверка запроса к несуществующей странице"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)
