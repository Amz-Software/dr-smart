# Generated by Django 4.2.16 on 2025-03-28 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assistencia', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='caixaassistencia',
            options={'permissions': [('view_assistencia', 'Pode visualizar assistência')], 'verbose_name_plural': 'Caixas'},
        ),
    ]
