# Generated by Django 4.2.16 on 2024-10-06 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('financeiro', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gastofixo',
            options={'verbose_name_plural': 'Gastos Fixos'},
        ),
        migrations.AddField(
            model_name='gastofixo',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gastofixo',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='gastofixo',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='gastofixo',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
