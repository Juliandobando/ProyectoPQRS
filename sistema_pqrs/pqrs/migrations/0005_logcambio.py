# Generated by Django 5.2.1 on 2025-05-19 05:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pqrs', '0004_administrador_cliente_activo_gestor_activo'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogCambio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('campo_modificado', models.CharField(max_length=50)),
                ('valor_anterior', models.TextField(blank=True, null=True)),
                ('valor_nuevo', models.TextField(blank=True, null=True)),
                ('gestor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='pqrs.gestor')),
                ('pqrs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pqrs.pqrs')),
            ],
        ),
    ]
