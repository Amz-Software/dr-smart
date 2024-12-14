from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        