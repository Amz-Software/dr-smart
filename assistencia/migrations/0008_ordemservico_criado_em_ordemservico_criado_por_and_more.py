# Generated by Django 4.2.16 on 2025-04-08 00:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assistencia', '0007_alter_ordemservico_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='criado_por',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='modificado_por',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
        ),
    ]
