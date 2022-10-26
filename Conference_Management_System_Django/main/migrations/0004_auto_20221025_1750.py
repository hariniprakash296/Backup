# Generated by Django 2.2.1 on 2022-10-25 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20221025_1718'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.User')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('main.user',),
        ),
        migrations.CreateModel(
            name='ConferenceChair',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.User')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('main.user',),
        ),
        migrations.CreateModel(
            name='SystemAdmin',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.User')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('main.user',),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.TextField(primary_key=True, serialize=False, unique=True),
        ),
    ]