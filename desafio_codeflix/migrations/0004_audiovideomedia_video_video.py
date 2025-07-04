# Generated by Django 5.2.3 on 2025-06-26 14:33

import desafio_codeflix.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('desafio_codeflix', '0003_category_genre_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioVideoMedia',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_path', models.CharField(max_length=255)),
                ('encoded_path', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('PROCESSING', 'PROCESSING'), ('COMPLETED', 'COMPLETED'), ('FAILED', 'FAILED')], default=desafio_codeflix.models.MediaStatus['PENDING'], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='video',
            name='video',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='video', to='desafio_codeflix.audiovideomedia'),
        ),
    ]
