# Generated by Django 5.0.3 on 2024-04-16 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0012_alter_user_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='house',
            name='available',
            field=models.BooleanField(default=True),
        ),
    ]
