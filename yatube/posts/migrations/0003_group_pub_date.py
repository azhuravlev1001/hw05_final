# Generated by Django 2.2.19 on 2022-09-04 13:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220829_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True,
                                       default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
