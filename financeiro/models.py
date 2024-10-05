from django.db import models

class GastoFixo(models.Model):
    nome = models.CharField(max_length=100)