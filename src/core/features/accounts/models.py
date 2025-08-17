from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

class UserManager(BaseUserManager):
    def create_user(self, social_id, email, name, provider, password=None, phone_number=None):
        if not social_id or not email:
            raise ValueError('소셜 ID와 이메일은 필수입니다.')
        user = self.model(
            social_id=social_id,
            email=self.normalize_email(email),
            name=name,
            provider=provider,
            phone_number=phone_number
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
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True)
    provider = models.CharField(max_length=30, null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # 권한 및 그룹 충돌 해결을 위한 필드 추가
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='accounts_user_groups',
        related_query_name='accounts_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='accounts_user_permissions',
        related_query_name='accounts_user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'social_id']  # 'social_id'를 추가

    objects = UserManager()

    def __str__(self):
        return self.email
