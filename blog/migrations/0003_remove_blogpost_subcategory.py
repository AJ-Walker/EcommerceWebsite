# Generated by Django 3.2 on 2021-06-11 13:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20210611_1844'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpost',
            name='subcategory',
        ),
    ]
