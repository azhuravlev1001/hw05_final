from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile

import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestImage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='azhuravlev1001')
        cls.group = Group.objects.create(
            title='Тестовый заголовок группы',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded_1 = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif_1,
            content_type='image/gif'
        )
        cls.new_post = Post.objects.create(
            text='Картинка в тестовом посте',
            group=cls.group,
            author=cls.author,
            image=cls.uploaded_1
        )
        small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif_2,
            content_type='image/gif'
        )

    def setUp(self):
        self.by_author = Client()
        self.by_author.force_login(TestImage.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.by_author = Client()
        self.by_author.force_login(TestImage.author)

    def test_UploadedImageGoesToDB(self):
        posts_count = Post.objects.count()
        self.by_author.post(reverse('posts:post_create'),
                            data={'text': 'Картинка и текст поста',
                                  'image': self.uploaded_2, },
                            follow=True)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Картинка и текст поста',
                image='posts/small_2.gif'
            ).exists()
        )

    def test_ImageWithinPostGoesToPages(self):
        self.assertEqual(TestImage.new_post.image, 'posts/small_1.gif')
        response = self.by_author.get('/')
        self.assertTrue(
            TestImage.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(
            f'/profile/{TestImage.new_post.author.username}/')
        self.assertTrue(
            TestImage.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(f'/group/{TestImage.group.slug}/')
        self.assertTrue(
            TestImage.new_post in
            response.context.get('page_obj').paginator.object_list
        )
        response = self.by_author.get(f'/posts/{TestImage.new_post.id}/')
        self.assertEqual(response.context.get('post'), TestImage.new_post)
