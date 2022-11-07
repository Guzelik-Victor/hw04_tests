# deals/tests/tests_form.py

from posts.forms import PostForm
from posts.models import Post, User
from django.test import Client, TestCase
from django.urls import reverse


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 2',
            ).exists()
        )

    def test_post_edit(self):
        """Автор поста редактуриет запись в Post."""
        form_data = {
            'text': 'Тестовый пост  - редактированный',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост  - редактированный',
            ).exists()
        )


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def test_help_text(self):
        text_help_text = PostFormTests.form.fields['text'].help_text
        self.assertEquals(text_help_text, 'Текст нового поста')
        text_help_group = PostFormTests.form.fields['group'].help_text
        self.assertEquals(text_help_group,
                          'Группа, к которой будет относиться пост')
