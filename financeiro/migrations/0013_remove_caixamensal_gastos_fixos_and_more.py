# Generated by Django 4.2.16 on 2024-12-15 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0012_remove_funcionario_caixa_mensal_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caixamensal',
            name='gastos_fixos',
        ),
        migrations.AddField(
            model_name='caixamensal',
            name='gasto_fixos',
            field=models.ManyToManyField(related_name='caixas_mensais', through='financeiro.CaixaMensalGastoFixo', to='financeiro.gastofixo'),
        ),
        migrations.AlterField(
            model_name='caixamensal',
            name='funcionarios',
            field=models.ManyToManyField(related_name='caixas_mensais', through='financeiro.CaixaMensalFuncionario', to='financeiro.funcionario'),
        ),
    ]
