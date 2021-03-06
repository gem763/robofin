# Generated by Django 2.2.2 on 2019-06-28 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=50)),
                ('ccy', models.CharField(max_length=50)),
                ('exchange', models.CharField(max_length=50)),
                ('time', models.DateTimeField()),
                ('close', models.FloatField()),
                ('high', models.FloatField()),
                ('low', models.FloatField()),
                ('open', models.FloatField()),
                ('volume', models.FloatField()),
                ('amount', models.FloatField()),
            ],
        ),
    ]
