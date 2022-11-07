from http import HTTPStatus
from django.test import TestCase, Client

from posts.models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Тестовая группа'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_not_authorized_client(self):
        """Страницы доступные всем пользователям."""
        url_available_to_any_user = {
            '/': HTTPStatus.OK,
            '/group/slug/': HTTPStatus.OK,
            '/profile/Thank_you/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/any/': HTTPStatus.NOT_FOUND
        }

        for url, expected in url_available_to_any_user.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected)

    def test_posts_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_url_exists_at_desired_location(self):
        """Страница /posts/edit/ доступна автору."""
        response = self.authorized_client.get('/posts/1/edit/')
        # Сверяем данные текущего пользователя с данными автора поста
        self.assertEqual(response.wsgi_request.user, self.post.author)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_anonymouson(self):
        """Страница /posts/create/ перенаправляет анонимного
        пользователя.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects
        (
            response, '/auth/login/?next=/create/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            '/profile/Thank_you/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)