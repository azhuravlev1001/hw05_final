from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
from ..models import Post, Follow
from django.urls import reverse


User = get_user_model()


class TestCash(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.user = User.objects.create_user(username='simple_user')

        cls.new_post = Post.objects.create(
            text='Новый пост в ленте',
            author=TestCash.author
        )

    def setUp(self):
        self.by_non_author = Client()
        self.by_non_author.force_login(TestCash.user)
        self.by_author = Client()
        self.by_author.force_login(TestCash.author)

    def test_CashAtIndexPageIsRunning(self):
        content_before_post = self.by_author.get('/').content
        Post.objects.create(
            text='Картинка в тестовом посте',
            author=TestCash.author
        )
        content_after_post = self.by_author.get('/').content
        self.assertEqual(content_before_post, content_after_post)
        cache.clear()
        content_after_clearing = self.by_author.get('/').content
        self.assertNotEqual(content_before_post, content_after_clearing)

    def test_AuthorFollowsUnfollowsOthers(self):
        count_before = Follow.objects.count()
        self.by_non_author.post(reverse(
            'posts:profile_follow',
            kwargs={'username': TestCash.author.username}))
        self.assertEqual(Follow.objects.count(), count_before + 1)
        self.by_non_author.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestCash.author.username}))
        self.assertEqual(Follow.objects.count(), count_before)

    def test_FollowerSeesNewPost(self):
        Follow.objects.get_or_create(
            user=TestCash.author,
            author=TestCash.author
        )
        response = self.by_author.get(reverse('posts:follow_index'))
        self.assertTrue(
            response.context.get('page_obj').paginator.object_list.filter(
                post=TestCash.new_post).exists()
        )
        self.by_author.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestCash.author.username}
        ))
        response = self.by_author.get(reverse('posts:follow_index'))
        self.assertFalse(
            response.context.get('page_obj').paginator.object_list.filter(
                post=TestCash.new_post).exists()
        )
