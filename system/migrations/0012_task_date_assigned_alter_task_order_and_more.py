# Generated by Django 4.1.3 on 2023-01-24 15:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0011_remove_task_date_assigned_task_date_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='date_assigned',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='order',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='system.orderservice'),
        ),
        migrations.AlterUniqueTogether(
            name='task',
            unique_together={('order', 'technician')},
        ),
    ]
