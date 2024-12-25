# Generated by Django 5.1.4 on 2024-12-25 09:59

import admin_dashboard.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('birth_date', models.CharField(max_length=10, validators=[admin_dashboard.models.validate_date_format])),
                ('gender', models.CharField(max_length=20)),
                ('adress', models.CharField(max_length=50)),
                ('telephone', models.CharField(max_length=20)),
            ],
        ),
    ]