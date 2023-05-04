"""
Database models
"""
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    """Extra fields are for any other fields that we want to pass in (like name, age, ...)."""

    def create_user(self, phone=None, password=None, **extra_fields):
        """Create a new user profile."""
        # if not phone:
        #     raise ValueError("Users must have an phone number.")
        user = self.model(phone=phone, **extra_fields)
        user.is_active = False
        """When using set_password, the password will be hashed before it is stored in the database."""
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
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

    email = models.EmailField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True, unique=True, default=None)
    verify_phone_otp = models.CharField(max_length=6, blank=True, null=True)
    reset_pass_otp = models.CharField(max_length=6, blank=True, null=True)
    address_1 = models.TextField(blank=True, null=True)
    address_2 = models.TextField(blank=True, null=True)
    address_3 = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    """Can login to the admin site."""
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    class Meta:
        constraints = [
            # For phone == null only
            models.UniqueConstraint(
                fields=["email"],
                name="unique__email__when__phone__null",
                condition=Q(phone__isnull=True),
            ),
            # For phone != null only
            models.UniqueConstraint(
                fields=["email", "phone"], name="unique__email__when__phone__not__null"
            ),
        ]

    """Replace default username field comes from django user with email field."""
    USERNAME_FIELD = "phone"
