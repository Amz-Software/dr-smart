from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)
    
    
    def save(self, *args, **kwargs):
            
        if self.first_name and self.last_name and not self.username:
            self.username = f"{self.first_name.lower()}.{self.last_name.lower()}"
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        permissions = [
            ('view_own_user', 'Can view own user')
        ]
        