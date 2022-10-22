from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Post, Comment

User = get_user_model()


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.new_post = Post.objects.create(
            text='Картинка в тестовом посте',
            author=cls.author,
        )
        cls.new_comment = Comment.objects.create(
            post=cls.new_post,
            author=cls.author,
            text='Тестовый комментарий'
        )

    def setUp(self):
        self.by_guest = Client()
        self.by_author = Client()
        self.by_author.force_login(TestComment.author)

    def test_CommentAppearsAtPostPage(self):
        self.assertEqual(TestComment.new_comment.text, 'Тестовый комментарий')
        response = self.by_author.get(f'/posts/{TestComment.new_post.id}/')
        self.assertTrue(TestComment.new_comment in
                        response.context.get('comments'))

    def test_GuestCannotLeaveComment(self):
        self.assertRedirects(
            self.by_guest.get(f'/posts/{TestComment.new_post.id}/comment/',
                              follow=True),
            f'/auth/login/?next=/posts/{TestComment.new_post.id}/comment/',
            status_code=302, target_status_code=200)
