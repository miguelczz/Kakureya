# Generated by Django 5.1.6 on 2025-03-30 04:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakureya', '0004_userprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(choices=[('sushi', 'Sushi'), ('ramen', 'Ramen'), ('yakitori', 'Yakitori'), ('donburi', 'Donburi'), ('postres', 'Postres'), ('sin categoría', 'Sin categoría')], default='Sin categoría', max_length=50),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('paypal', 'PayPal'), ('credit_card', 'Tarjeta de Crédito'), ('cash', 'Efectivo')], default='paypal', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
