# Generated by Django 3.1.7 on 2021-03-31 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('speedtest', '0004_auto_20210330_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='locations',
            name='color',
            field=models.CharField(default='rgb(255,255,255)', max_length=200),
        ),
    ]
