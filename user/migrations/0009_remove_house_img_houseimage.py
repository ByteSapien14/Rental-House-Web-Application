# Generated by Django 5.0.3 on 2024-04-16 16:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_alter_house_kitchen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='house',
            name='img',
        ),
        migrations.CreateModel(
            name='HouseImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='house_images/')),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='user.house')),
            ],
        ),
    ]
