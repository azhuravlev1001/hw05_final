from django import forms

GROUP_FIELDS_NAME_TYPE = {
    'title': 'CharField',
    'slug': 'SlugField',
    'description': 'TextField',
}

POST_FIELDS_NAME_TYPE = {
    'text': 'TextField',
    'pub_date': 'DateTimeField',
    'author': 'ForeignKey',
    'group': 'ForeignKey',
}

EXPECTED_POST_VERB_NAME = {
    'pub_date': 'Дата публикации',
    'author': 'Автор поста',
    'text': 'Текст поста',
    'group': 'Сообщество',
}

EXPECTED_POST_HELP_TEXT = {
    'pub_date': 'Дата публикации (ставится автоматически)',
    'author': 'Автор поста',
    'text': 'Введите текст поста',
    'group': 'Укажите, к какой группе относится пост',
}

EXPECTED_GROUP_VERB_NAME = {
    'title': 'Название группы',
    'slug': 'Адрес группы',
    'description': 'Описание группы',
}

EXPECTED_GROUP_HELP_TEXT = {
    'title': 'Укажите название группы',
    'slug': (
        'Укажите уникальный адрес для страницы группы. '
        'Используйте только латиницу, '
        'цифры, дефисы и знаки подчёркивания'),
    'description': 'Добавьте описание группы',
}

POST_MODEL_DICT = {
    'verbose_name': EXPECTED_POST_VERB_NAME,
    'help_text': EXPECTED_POST_HELP_TEXT,
}

GROUP_MODEL_DICT = {
    'verbose_name': EXPECTED_GROUP_VERB_NAME,
    'help_text': EXPECTED_GROUP_HELP_TEXT,
}

FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.fields.ChoiceField,
}


def ValidateFields(self, object, field_name_type):
    for field_name, field_type in field_name_type.items():
        with self.subTest(field_name=field_name):
            self.assertEqual(
                object._meta.get_field(field_name).get_internal_type(),
                field_type
            )


def CheckNameAndText(self, checked_object, checked_attr, expected_value_dict):
    """Проверка корректности verbose_name и help_text в моделях"""

    for field, expected_value in expected_value_dict.items():
        attr_dict = {
            'verbose_name': checked_object._meta.get_field(field).verbose_name,
            'help_text': checked_object._meta.get_field(field).help_text,
        }
        real_value = attr_dict[checked_attr]
        with self.subTest(field=field):
            self.assertEqual(real_value, expected_value)


def get_response(at_address, by_client, *args, **kwargs):
    response = by_client.get(at_address, *args, **kwargs)
    return response


def GetField(name, at_address, by_client):
    response = get_response(at_address, by_client)
    form_field = response.context.get('form').fields.get(name)
    return form_field
