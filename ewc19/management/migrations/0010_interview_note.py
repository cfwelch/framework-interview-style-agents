# Generated by Django 4.1.1 on 2022-12-25 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_rename_interview_id_question_interview'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='note',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]