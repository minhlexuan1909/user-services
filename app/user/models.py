"""
Database models
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    """Extra fields are for any other fields that we want to pass in (like name, age, ...)."""

    def create_user(self, email, password=None, **extra_fields):
        """Create a new user profile."""
        if not email:
            raise ValueError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        """When using set_password, the password will be hashed before it is stored in the database."""
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser with given details."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    address_1 = models.TextField(blank=True, null=True)
    address_2 = models.TextField(blank=True, null=True)
    address_3 = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    """Can login to the admin site."""
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    """Replace default username field comes from django user with email field."""
    USERNAME_FIELD = "email"
