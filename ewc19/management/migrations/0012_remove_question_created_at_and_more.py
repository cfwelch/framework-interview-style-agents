# Generated by Django 4.1.1 on 2022-12-26 12:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_interview_respect_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='question',
            name='updated_at',
        ),
    ]
