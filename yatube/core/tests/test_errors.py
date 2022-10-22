from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class TestErrors(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='leo')

    def setUp(self):
        self.by_author = Client()
        self.by_author.force_login(TestErrors.author)

    def test_Error404HasCustomTemplate(self):
        self.assertTemplateUsed(self.by_author.get('non-existing-page'),
                                'core/404.html')
