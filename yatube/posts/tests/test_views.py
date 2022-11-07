# deals/tests/test_views.py
from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User
from posts.views import POSTS_PER_PAGE

POSTS_FOR_PAGINATOR_TEST = 13
POSTS_PER_PAGE_TEST = 3
INDEX_ZERO = 0
NUMBER_OF_TEMPLATES = 2


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Тестовая группа'
        )
        cls.group_test = Group.objects.create(
            title='Группа без постов',
            slug='any_slug',
            description='Тестовая группа для дополнительного задания'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
            (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.post.author}):
            (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            (
                'posts/create_post.html'
            ),
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Дополнительная проверка при создании поста - в этой функции
    def test_correct_working_context(self):
        """Шаблон index, group_list, profile
        сформированы с правильным контекстом.
        При создании поста, он появляется на этих страницах."""
        list_of_templates = [
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get
            (
                reverse('posts:group_list',
                        kwargs={'slug': self.group.slug}
                        )
            ),
            self.authorized_client.get
            (
                reverse('posts:profile',
                        kwargs={'username': self.post.author}
                        )
            ),
        ]
        for templates in list_of_templates:
            response = templates
            first_object = response.context['page_obj'][INDEX_ZERO]
            self.assertEqual(first_object.text, self.post.text)
            self.assertEqual(first_object.author, self.post.author)
            self.assertEqual(first_object.group, self.post.group)

    def test_additional_verification_when_creating_a_post(self):
        """Пост не попадает в группу, для которой не был предназначен."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group_test.slug})
        )
        post_test_group = response.context.get('page_obj').object_list
        self.assertEqual(post_test_group.count(), INDEX_ZERO)

    def test_correct_working_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_post_create_and_edit_correct_context(self):
        """Шаблоны post_create, post_edit сформированы
        с правильным контекстом."""
        list_of_templates = [
            self.authorized_client.get(reverse('posts:post_create')),
            self.authorized_client.get(reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk})
            )
        ]
        # поля pub_date, author формирует Django - ему мы доверяем!)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for templates in list_of_templates:
            response = templates
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Тестовая группа'
        )
        list_post = []
        for post_number in range(POSTS_FOR_PAGINATOR_TEST):
            list_post.append(
                Post(
                    text=f'Тестовый пост № {post_number}',
                    author=cls.user,
                    group=cls.group,
                )
            )
        cls.posts = Post.objects.bulk_create(list_post)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records(self):
        list_of_templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.posts[INDEX_ZERO].author}),
        ]
        for template in list_of_templates:
            response = self.authorized_client.get(template)
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
            response = self.authorized_client.get(template + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), POSTS_PER_PAGE_TEST
            )
