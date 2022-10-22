from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import STR_LENGTH, Group, Post
from .test_store import (GROUP_FIELDS_NAME_TYPE, GROUP_MODEL_DICT,
                         POST_FIELDS_NAME_TYPE, POST_MODEL_DICT,
                         CheckNameAndText, ValidateFields)

User = get_user_model()


class PostModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='ж' * 50,
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group)

    def test_GroupHasCorrectFieldTypes(self):
        ValidateFields(self, PostModel.group, GROUP_FIELDS_NAME_TYPE)

    def test_GroupHasCorrect__str__(self):
        self.assertEqual(PostModel.group.title, str(PostModel.group))

    def test_GroupHasCorrectVerbNameAndHelpText(self):
        for attr_name, value in GROUP_MODEL_DICT.items():
            with self.subTest(attr_name=attr_name):
                CheckNameAndText(self, PostModel.group, attr_name, value)

    def test_PostHasCorrectFieldTypes(self):
        ValidateFields(self, PostModel.post, POST_FIELDS_NAME_TYPE)

    def test_PostHasCorrect__str__(self):
        self.assertEqual(PostModel.post.text[:STR_LENGTH], str(PostModel.post))

    def test_PostHasCorrectVerbNameAndHelpText(self):
        for attr_name, value in POST_MODEL_DICT.items():
            with self.subTest(attr_name=attr_name):
                CheckNameAndText(self, PostModel.post, attr_name, value)
