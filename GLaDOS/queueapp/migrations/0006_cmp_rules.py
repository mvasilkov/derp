# Generated by Django 2.0.3 on 2018-07-02 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queueapp', '0005_multiple_counts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buffer',
            name='cmp_rules',
            field=models.TextField(blank=True),
        ),
    ]