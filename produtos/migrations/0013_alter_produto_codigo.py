# Generated by Django 4.2.16 on 2025-01-08 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0012_alter_produto_codigo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='codigo',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
    ]
