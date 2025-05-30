# Generated by Django 4.2.16 on 2024-10-06 15:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='corproduto',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='corproduto',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='corproduto',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='corproduto',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estadoproduto',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estadoproduto',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estadoproduto',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='estadoproduto',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fabricante',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fabricante',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fabricante',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='fabricante',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='memoriaproduto',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='memoriaproduto',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='memoriaproduto',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='memoriaproduto',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produto',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produto',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produto',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tipoproduto',
            name='criado_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tipoproduto',
            name='criado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_criadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tipoproduto',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tipoproduto',
            name='modificado_por',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s_modificadas', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
