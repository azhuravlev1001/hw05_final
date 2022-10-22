from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..views import COUNT_OF_POSTS_ON_PAGE
from .test_store import FORM_FIELDS, GetField, get_response

User = get_user_model()


class Views(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        cls.new_group = Group.objects.create(
            title='Тестовая группа',
            slug='new_group',
            description='Группа 2 для новых постов'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group,
            id=2
        )

        cls.new_post = Post.objects.create(
            text='Тестовый пост с Группой 2',
            author=cls.author,
            group=cls.new_group
        )

        global PATHS_PAGES, AT_PAGE, COUNT_OF_POSTS

        COUNT_OF_POSTS = 16

        PATHS_PAGES = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:posts', kwargs={'slug': getattr(Views.group, 'slug')}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': getattr(Views.post,
                                         'author')}
            ): 'posts/profile.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': getattr(Views.post,
                                           'id')}
            ): 'posts/create_post.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': getattr(Views.post,
                                             'id')}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        AT_PAGE = {
            '/create': reverse('posts:post_create'),
            '/edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': getattr(Views.post, 'id')}),
            '/<post_id>': reverse(
                'posts:post_detail',
                kwargs={'post_id': getattr(Views.post, 'id')}),
            '/group/<slug>': reverse(
                'posts:posts',
                kwargs={'slug': getattr(Views.group, 'slug')}),
            '/profile/<username>': reverse(
                'posts:profile',
                kwargs={'username': getattr(Views.post, 'author')}),
            '/': reverse('posts:index'),
        }

        for i in range(COUNT_OF_POSTS - 2):
            Post.objects.create(text=f'Тестовый текст поста_{i}',
                                author=cls.author, group=cls.group)

    def setUp(self):
        self.guest = Client()
        self.by_author = Client()
        self.by_author.force_login(Views.author)

    def test_TemplatesMatchShortcuts(self):
        for path_to_page, template in PATHS_PAGES.items():
            with self.subTest(template=template):
                self.assertTemplateUsed(
                    get_response(path_to_page, self.by_author), template)

    def test_FormsHaveCorrectFieldTypes(self):
        for of_name, fieldtype_to_be in FORM_FIELDS.items():
            with self.subTest(name=of_name):
                self.assertIsInstance(
                    GetField(of_name, AT_PAGE['/create'], self.by_author),
                    fieldtype_to_be)
                self.assertIsInstance(
                    GetField(of_name, AT_PAGE['/edit'], self.by_author),
                    fieldtype_to_be)

    def test_PostPageHasCorrectContext(self):
        response = self.by_author.get(AT_PAGE['/<post_id>'])
        self.assertEqual(response.context.get('post'), Views.post)

    def test_GroupPageHasCorrectContext(self):
        response = self.by_author.get(AT_PAGE['/group/<slug>'])
        self.assertEqual(response.context.get('group'), Views.group)

    def test_ProfilePageHasCorrectContext(self):
        response = self.by_author.get(AT_PAGE['/profile/<username>'])
        self.assertEqual(response.context.get('author'), Views.author)

    def test_PaginatorWorksAtIndexPage(self):
        response = self.by_author.get(AT_PAGE['/'])
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS_ON_PAGE)
        response = self.by_author.get(AT_PAGE['/'] + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS - COUNT_OF_POSTS_ON_PAGE)

    def test_PaginatorWorksAtGroupPage(self):
        response = self.by_author.get(AT_PAGE['/group/<slug>'])
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS_ON_PAGE)
        response = self.by_author.get(AT_PAGE['/group/<slug>'] + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS - COUNT_OF_POSTS_ON_PAGE - 1)

    def test_PaginatorWorksAtProfilePage(self):
        response = self.by_author.get(AT_PAGE['/profile/<username>'])
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS_ON_PAGE)
        response = self.by_author.get(
            AT_PAGE['/profile/<username>'] + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            COUNT_OF_POSTS - COUNT_OF_POSTS_ON_PAGE)

    def test_NewPostBehaviour(self):
        response = self.by_author.get('/')
        self.assertEqual(Views.new_post.group, Views.new_group)
        self.assertTrue(
            Views.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(f'/group/{Views.new_group.slug}/')
        self.assertTrue(
            Views.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(
            f'/profile/{Views.new_post.author.username}/')
        self.assertTrue(
            Views.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(f'/group/{Views.group.slug}/')
        self.assertFalse(
            Views.new_post in
            response.context.get('page_obj').paginator.object_list
        )
