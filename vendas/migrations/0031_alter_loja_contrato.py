# Generated by Django 4.2.16 on 2025-01-09 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0030_alter_loja_contrato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='contrato',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
