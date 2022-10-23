from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from ..models import Post, Follow
from django.urls import reverse


User = get_user_model()


class TestSubscription(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.user = User.objects.create_user(username='simple_user')
        cls.unauthorised = User.objects.create_user(username='unauthorised')

        cls.new_post = Post.objects.create(
            text='Новый пост в ленте',
            author=TestSubscription.author
        )

    def setUp(self):
        self.by_unauthorised = Client()
        self.by_non_author = Client()
        self.by_non_author.force_login(TestSubscription.user)
        self.by_author = Client()
        self.by_author.force_login(TestSubscription.author)

    def test_AuthorFollowsOthers(self):
        self.by_non_author.post(reverse(
            'posts:profile_follow',
            kwargs={'username': TestSubscription.author.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=TestSubscription.author).exists())

    def test_UnauthorisedCannotFollow(self):
        self.by_unauthorised.post(reverse(
            'posts:profile_follow',
            kwargs={'username': TestSubscription.author.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=TestSubscription.unauthorised, author=TestSubscription.author).exists())

    def test_AuthorUnfollowsOthers(self):
        self.by_non_author.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestSubscription.author.username}
        ))
        self.assertFalse(Follow.objects.all())

    def test_UnauthorisedCannotUnfollow(self):
        Follow.objects.create(user=self.user, author=TestSubscription.author)
        self.by_unauthorised.post(reverse(
            'posts:profile_unfollow',
            kwargs={'username': TestSubscription.author.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=TestSubscription.author).exists())

    def test_FollowerSeesNewPost(self):
        Follow.objects.create(
            user=TestSubscription.author,
            author=TestSubscription.author
        )
        response = self.by_author.get(reverse('posts:follow_index'))
        self.assertTrue(
            response.context.get('page_obj').paginator.object_list.filter(
                text=TestSubscription.new_post.text).exists()
        )
        TestSubscription.new_post.delete()
        response = self.by_author.get(reverse('posts:follow_index'))
        self.assertFalse(
            response.context.get('page_obj').paginator.object_list.filter(
                text=TestSubscription.new_post.text).exists()
        )

    def test_UnauthorisedCannotOpenFollowList(self):
        response = self.by_unauthorised.get(reverse('posts:follow_index'))
        self.assertFalse(response.status_code == 200)
