# Generated by Django 4.1 on 2024-03-27 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("theatre_booking", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="performance",
            name="theatre_hall",
        ),
        migrations.AddField(
            model_name="performance",
            name="theatre_hall",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="theatre_booking.theatrehall",
            ),
        ),
    ]
