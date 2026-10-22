from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ProjectB's independent user table for warehouse operators."""

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
