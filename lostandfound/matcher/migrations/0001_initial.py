# Generated by Django 5.0.2 on 2025-04-11 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('items', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureVector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vector', models.BinaryField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feature_vector', to='items.item')),
            ],
        ),
    ]
