# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, social_id, email, name, password=None):
        if not social_id or not email:
            raise ValueError('소셜 ID와 이메일은 필수입니다.')
        user = self.model(
            social_id=social_id,
            email=self.normalize_email(email),
            name=name
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, social_id, email, name, password=None):
        user = self.create_user(
            social_id=social_id,
            email=email,
            name=name
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    social_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['social_id', 'name']

    objects = UserManager()

    def __str__(self):
        return self.email
