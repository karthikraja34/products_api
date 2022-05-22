# Generated by Django 3.2.13 on 2022-05-22 08:50

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='Product name')),
                ('sku', models.CharField(max_length=300, unique=True, verbose_name='SKU')),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
