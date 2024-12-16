# Generated by Django 4.1.1 on 2022-11-30 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LDA',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('startingDate', models.DateTimeField()),
                ('endingDate', models.DateTimeField()),
                ('duration', models.DecimalField(decimal_places=3, max_digits=10)),
                ('status', models.CharField(max_length=300)),
                ('corpusFile', models.CharField(max_length=500)),
                ('outputFile', models.CharField(max_length=500)),
                ('topic', models.CharField(max_length=50)),
            ],
        ),
    ]
