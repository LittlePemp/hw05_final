import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-test',
            description='Тестовое описание')

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')

        cls.author = User.objects.create_user(username='Poster')
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.author)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author,
            group=cls.group,
            image=uploaded)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.templates_pages_names = {
            'index.html': reverse('posts:index'),
            'processing_post.html': reverse('posts:new_post'),
            'group.html': reverse(
                'posts:group',
                kwargs={'slug': PostPagesTests.group.slug}),
            'profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.author.username}),
            'post.html': reverse(
                'posts:post',
                kwargs={
                    'username': PostPagesTests.author.username,
                    'post_id': PostPagesTests.post.id})}

    def test_pages_use_correct_template(self):
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page'][0]
        self.check_post(post)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': PostPagesTests.post.author.username}))
        post = response.context['page'][0]
        self.check_post(post)

    def test_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post',
            kwargs={
                'username': PostPagesTests.author.username,
                'post_id': PostPagesTests.post.id}))
        post = response.context['post']
        self.check_post(post)

    def test_group_shows_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': PostPagesTests.group.slug}))
        group_object = response.context['group']
        group_title = group_object.title
        group_description = group_object.description
        self.assertEqual(group_title, PostPagesTests.group.title)
        self.assertEqual(group_description, PostPagesTests.group.description)
        post = response.context['page'][0]
        self.check_post(post)

    def test_cache_index(self):
        self.authorized_client.get(reverse('posts:index'))
        form_data = {'text': 'Text2'}
        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'username': PostPagesTests.post.author.username,
                    'post_id': PostPagesTests.post.id}),
            data=form_data,
            follow=True)
        key = make_template_fragment_key('index_page')
        self.assertIsNotNone(cache.get(key))
        cache.clear()
        self.test_index_shows_correct_context()

    def test_follow(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostPagesTests.author.username}))
        self.assertTrue(
            Follow.objects.filter(
                author=PostPagesTests.author,
                user=self.user).exists())

    def test_unfollow(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostPagesTests.author.username}))
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostPagesTests.author.username}))
        self.assertFalse(
            Follow.objects.filter(
                author=PostPagesTests.author,
                user=self.user).exists())

    def test_follow_index(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostPagesTests.author.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post = response.context['page'][0]
        self.check_post(post)

    def check_post(self, post):
        post_text = post.text
        post_author = post.author
        post_group = post.group
        post_image = post.image
        self.assertEqual(post_text, PostPagesTests.post.text)
        self.assertEqual(post_author, PostPagesTests.post.author)
        self.assertEqual(post_group, PostPagesTests.post.group)
        self.assertEqual(post_image, PostPagesTests.post.image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-test',
            description='Тестовое описание',
        )
        cls.author = User.objects.create_user(username='Poster')
        authorized_client = Client()
        authorized_client.force_login(cls.author)
        for i in range(13):
            Post.objects.create(
                text='t' * (i + 1),
                author=cls.author,
                group=cls.group)

    def test_first_page_contains_ten_records(self):
        paginators = [
            reverse('posts:index'),
            reverse(
                'posts:group',
                kwargs={'slug': PaginatorViewsTest.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author.username})]
        for link in paginators:
            response = self.client.get(link)
            self.assertEqual(
                len(response.context.get('page').object_list),
                10)
            response = self.client.get(link + '?page=2')
            self.assertEqual(
                len(response.context.get('page').object_list),
                3)
