# Generated by Django 5.1.4 on 2024-12-25 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_dashboard', '0003_alter_patient_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]