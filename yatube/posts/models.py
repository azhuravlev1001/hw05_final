from django.contrib.auth import get_user_model
from django.db import models

STR_LENGTH = 15

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название группы',
        max_length=200,
        help_text='Укажите название группы')
    slug = models.SlugField(
        verbose_name='Адрес группы',
        max_length=50,
        unique=True,
        blank=True,
        help_text=(
            'Укажите уникальный адрес для страницы группы. '
            'Используйте только латиницу, цифры, дефисы и знаки подчёркивания'
        ))
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Добавьте описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации (ставится автоматически)'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор поста',
        related_name='posts',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Укажите, к какой группе относится пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:STR_LENGTH]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
        help_text='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
        help_text='Автор комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True,
        help_text='Дата комментария (ставится автоматически)'
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:STR_LENGTH]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписавшийся',
        help_text='Пользователь, который подписывается на автора'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['-user']
        unique_together = ('user', 'author')

    def __str__(self):
        return self.user.username
