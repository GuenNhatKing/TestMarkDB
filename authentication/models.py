from django.db import models

# Create your models here.
class UserAccount(models.Model):
    username = models.CharField(max_length=64, unique=True)
    salt = models.BinaryField(max_length=32)
    hashed = models.CharField(max_length=64)

    def __str__(self):
        return self.username