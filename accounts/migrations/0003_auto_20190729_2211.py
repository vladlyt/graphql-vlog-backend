# Generated by Django 2.2.2 on 2019-07-29 19:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0002_auto_20190729_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
