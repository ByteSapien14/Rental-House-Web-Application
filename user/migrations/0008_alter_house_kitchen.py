# Generated by Django 5.0.3 on 2024-04-16 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_delete_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='kitchen',
            field=models.CharField(max_length=20),
        ),
    ]
