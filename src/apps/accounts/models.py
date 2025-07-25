from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, social_id, email, name, provider, password=None):
        if not social_id or not email:
            raise ValueError('소셜 ID와 이메일은 필수입니다.')
        user = self.model(
            social_id=social_id,
            email=self.normalize_email(email),
            name=name,
            provider=provider or ""
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, social_id, email, name, provider='admin', password=None):
        user = self.create_user(
            social_id=social_id,
            email=email,
            name=name,
            provider=provider
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    social_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)

    # ✅ PostgreSQL에 적합하도록 null 대신 빈 문자열을 기본값으로
    provider = models.CharField(max_length=30, default="", blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['social_id', 'name', 'provider']

    objects = UserManager()

    def __str__(self):
        return self.email