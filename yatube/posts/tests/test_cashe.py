from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
from ..models import Post


User = get_user_model()


class TestCashe(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')

        cls.new_post = Post.objects.create(
            text='Новый пост в ленте',
            author=TestCashe.author
        )

    def setUp(self):
        self.by_author = Client()
        self.by_author.force_login(TestCashe.author)

    def test_CasheAtIndexPageIsRunning(self):
        content_before_post = self.by_author.get('/').content
        Post.objects.create(
            text='Картинка в тестовом посте',
            author=TestCashe.author
        )
        content_after_post = self.by_author.get('/').content
        self.assertEqual(content_before_post, content_after_post)
        cache.clear()
        content_after_clearing = self.by_author.get('/').content
        self.assertNotEqual(content_before_post, content_after_clearing)
