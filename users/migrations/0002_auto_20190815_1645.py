# Generated by Django 2.1.5 on 2019-08-15 16:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=40, null=True)),
                ('phone', models.CharField(max_length=20)),
                ('code', models.CharField(blank=True, max_length=12, null=True)),
                ('secret_generated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('code_approved', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='phone_secret',
        ),
        migrations.RemoveField(
            model_name='user',
            name='secret_generated_at',
        ),
        migrations.AddField(
            model_name='user',
            name='welcome_email',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
