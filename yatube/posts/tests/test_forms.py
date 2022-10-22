from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class Form(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.by_author = Client()
        self.by_author.force_login(Form.author)

    def test_SentFormMakesNewPost(self):
        posts_count = Post.objects.count()
        response = self.by_author.post(
            reverse('posts:post_create'),
            data={'text': 'Текст из формы'}, follow=True)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': Form.author.username}),
            status_code=302, target_status_code=200
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
                        text='Текст из формы',
                        author=Form.author,
                        group=None).exists())

    def test_EditedFormChangesPost(self):
        self.by_author.post(reverse('posts:post_edit',
                            kwargs={'post_id': Form.post.id}),
                            data={'text': 'Отредактированный текст'})
        self.assertTrue(Post.objects.filter(
                        id=Form.post.id,
                        text='Отредактированный текст',
                        author=Form.author,
                        group=None))
