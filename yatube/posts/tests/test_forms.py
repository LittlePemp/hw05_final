import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Post, Group, User, Comment


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-tost',
            description='Тестовое описание',
        )
        cls.group_red = Group.objects.create(
            title='Test group for redacted',
            slug='test-tost-red',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.user_fake = User.objects.create_user(username='Faker')
        self.authorized_fake = Client()
        self.authorized_fake.force_login(self.user_fake)

        self.guest_client = Client()

        self.non_redacts = [self.authorized_fake, self.guest_client]

        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')

        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif')

        self.post = Post.objects.create(
            text='Ж' * 10,
            author=self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.latest('id')
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.author, self.user)
        self.assertTrue(Post.objects.filter(image='posts/small.gif').exists())

    def test_redact_post_authorized(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст РЕДАКТИРОВАННЫЙ',
            'group': PostCreateFormTests.group_red.id,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'username': self.user.username, 'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post',
            kwargs={'username': self.user.username, 'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        last_post = Post.objects.latest('id')
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])

    def test_guest_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse('posts:new_post'))
        self.assertEqual(Post.objects.count(), posts_count)

    def test_redact_post_not_author(self):
        form_data = {'text': 'CLOSED'}
        for not_redact_client in self.non_redacts:
            response = not_redact_client.post(
                reverse(
                    'posts:post_edit',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id}),
                data=form_data,
                follow=True)
            self.assertRedirects(response, reverse(
                'posts:post',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id}))
            last_post = Post.objects.latest('id')
            self.assertEqual(last_post.text, self.post.text)

    def test_not_authorizated_comment(self):
        comments_cnt = Comment.objects.all().count()
        form_data = {'text': 'CLOSED'}
        response = self.guest_client.post(reverse(
            'posts:add_comment',
            kwargs={
                'username': self.user.username,
                'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse(
                'posts:add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id}))
        comments_cnt_after_fake_response = Comment.objects.all().count()
        self.assertEqual(comments_cnt_after_fake_response, comments_cnt)
