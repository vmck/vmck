# Generated by Django 2.2.4 on 2019-08-14 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vmck', '0003_auto_20190504_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='name',
            field=models.CharField(default='default', max_length=1024),
        ),
    ]
