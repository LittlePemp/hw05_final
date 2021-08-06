from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Введите название группы')
    slug = models.SlugField(max_length=100,
                            unique=True,
                            verbose_name='Краткая ссылочка',
                            help_text='Введите краткое название ссылочки')
    description = models.TextField(max_length=200,
                                   verbose_name='Описание',
                                   help_text=('Опишите, чем примечательна'
                                              ' ваша группа'))

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(max_length=200,
                            verbose_name='Пост',
                            help_text='Введите содержимое поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group,
                              verbose_name='Группа',
                              help_text=('Выберите группу,'
                                         ' в которой опубликуется пост'),
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    text = models.TextField(max_length=200,
                            verbose_name='Комментарий')
    created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')

    post = models.ForeignKey(Post,
                             verbose_name='Пост',
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True,
                             related_name='comments')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        ordering = ('-user',)
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'user',
                    'author'],
                name='uniques')]

    def __str__(self):
        return f'{self.user} -> {self.author}'
