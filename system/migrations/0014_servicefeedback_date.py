# Generated by Django 4.1.3 on 2023-01-24 16:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0013_servicefeedback'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicefeedback',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
