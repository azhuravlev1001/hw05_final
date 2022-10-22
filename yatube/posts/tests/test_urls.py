from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from .test_store import get_response

User = get_user_model()


class URL(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='azhuravlev1001')
        cls.author = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
            id=1
        )

        global URL_GUEST_WANTS_AND_GETS, URL_LIST, URL_NOT_FOR_GUEST
        global URL_TEMPLATES

        URL_TEMPLATES = {
            '/': 'posts/index.html',
            f'/group/{URL.group.slug}/': 'posts/group_list.html',
            f'/profile/{URL.user.username}/': 'posts/profile.html',
            f'/posts/{URL.post.id}/edit/': 'posts/create_post.html',
            f'/posts/{URL.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html'
        }

        URL_LIST = (
            '/',
            f'/group/{URL.group.slug}/',
            f'/profile/{URL.user.username}/',
            f'/posts/{URL.post.id}/edit/',
            f'/posts/{URL.post.id}/',
            '/create/'
        )

        URL_NOT_FOR_GUEST = (
            f'/posts/{URL.post.id}/edit/',
            '/create/'
        )

        URL_GUEST_WANTS_AND_GETS = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{URL.post.id}/edit/':
            f'/auth/login/?next=%2Fposts%2F{URL.post.id}%2Fedit%2F'
        }

    def setUp(self):
        self.by_guest = Client()
        self.by_non_author = Client()
        self.by_non_author.force_login(URL.user)
        self.by_author = Client()
        self.by_author.force_login(URL.author)

    def test_EachPageCanOpen(self):
        for at_address in URL_LIST:
            with self.subTest(address=at_address):
                self.assertEqual(
                    get_response(at_address, self.by_author).status_code,
                    200)

    def test_GuestCannotOpenPages(self):
        for at_address in URL_NOT_FOR_GUEST:
            with self.subTest(address=at_address):
                self.assertNotEqual(
                    get_response(at_address, self.by_guest).status_code, 200)

    def test_TemplatesMatchAddresses(self):
        for at_address, template in URL_TEMPLATES.items():
            with self.subTest(address=at_address):
                self.assertTemplateUsed(
                    get_response(at_address, self.by_author), template)

    def test_GuestGoesRedirected(self):
        for at_address, end_address in URL_GUEST_WANTS_AND_GETS.items():
            with self.subTest(address=at_address):
                self.assertRedirects(
                    get_response(at_address, self.by_guest, follow=True),
                    end_address, status_code=302, target_status_code=200)

    def test_WrongPageHasError404(self):
        self.assertEqual(
            get_response('/null_page/', self.by_author).status_code, 404)

    def test_OnlyAuthorCanEdit(self):
        at_address = URL_LIST[3]
        self.assertEqual(
            get_response(at_address, self.by_author).status_code,
            200, 'автор не смог открыть эту страницу')
        self.assertNotEqual(
            get_response(at_address, self.by_non_author).status_code,
            200, 'зарегистрированный не-автор смог открыть')
        self.assertNotEqual(
            get_response(at_address, self.by_guest).status_code,
            200, 'гость смог открыть')
