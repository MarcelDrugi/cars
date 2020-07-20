# Generated by Django 3.0.7 on 2020-07-16 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('car_rental', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segments',
            name='pricing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='segment_pricing', to='car_rental.PriceLists'),
        ),
    ]