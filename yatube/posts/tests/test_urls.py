from django.test import TestCase, Client
from posts.models import User, Group
from django.urls import reverse
from http import HTTPStatus


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_url_names = {
            'index.html': reverse('posts:index'),
            'processing_post.html': reverse('posts:new_post'),
            'group.html': reverse(
                'posts:group',
                kwargs={'slug': PostsURLTests.group.slug}),
        }

    def test_homepage(self):
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_groups_URL_anyone(self):
        response = self.guest_client.get(reverse(
            'posts:group',
            kwargs={'slug': PostsURLTests.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_new_url_redirect_anonymous_on_login(self):
        """New для неавторизованного"""
        response = self.guest_client.get(
            reverse('posts:new_post'),
            follow=True)
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse('posts:new_post'))

    def test_task_list_url_exists_at_desired_location(self):
        """New для авторизованного"""
        response = self.authorized_client.get(reverse('posts:new_post'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_404(self):
        response = self.guest_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'undefined_username'}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
