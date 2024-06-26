# Generated by Django 5.0.3 on 2024-04-22 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_house_payment_method_house_payment_option'),
    ]

    operations = [
        migrations.AlterField(
            model_name='house',
            name='payment_method',
            field=models.CharField(choices=[('mobile_money', 'Mobile Money'), ('credit_card', 'Credit Card')], max_length=100),
        ),
        migrations.AlterField(
            model_name='house',
            name='payment_option',
            field=models.CharField(choices=[('flat_fee', 'House Fee Per Advert (20,000)'), ('subscription', 'Subscription Plan (100,000 Yearly)')], max_length=100),
        ),
    ]
