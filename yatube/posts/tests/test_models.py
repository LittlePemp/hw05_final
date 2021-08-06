from django.test import TestCase
from posts.models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='tester')
        cls.post = Post.objects.create(
            text='Ж' * 100,
            author=author,
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Пост',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите содержимое поста',
            'group': 'Выберите группу, в которой опубликуется пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_str(self):
        post = PostModelTest.post
        excepted = PostModelTest.post.text[:15]
        self.assertEqual(str(post), excepted)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Ж' * 200,
            slug='task-task',
            description='Тестовый текст',
        )

    def test_verbose_name(self):
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Краткая ссылочка',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите краткое название ссылочки',
            'description': 'Опишите, чем примечательна ваша группа',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str(self):
        group = GroupModelTest.group
        group_str = str(group)
        self.assertEqual(group.title, group_str)
