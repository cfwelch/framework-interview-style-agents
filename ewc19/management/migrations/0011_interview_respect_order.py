# Generated by Django 4.1.1 on 2022-12-25 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_interview_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='respect_order',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
