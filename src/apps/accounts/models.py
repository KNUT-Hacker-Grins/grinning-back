# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, social_id, email, name, provider, password=None, phone_number=None): # phone_number 인자 추가
        if not social_id or not email:
            raise ValueError('소셜 ID와 이메일은 필수입니다.')
        user = self.model(
            social_id=social_id,
            email=self.normalize_email(email),
            name=name,
            provider=provider,
            phone_number=phone_number # phone_number 필드 설정
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, phone_number=None):
        social_id = email
        provider = 'admin'

        user = self.create_user(
            social_id=social_id,
            email=email,
            name=name,
            provider=provider,
            password=password,
            phone_number=phone_number
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    social_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True) # 전화번호 필드 추가
    provider = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email