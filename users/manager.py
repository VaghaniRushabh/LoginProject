from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Base User Manager to customise Django Auth User model
    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Please provide valid Email Address.")
        if not password:
            raise ValueError("Please provide a Password")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        user = self.create_user(email=email, password=password, **extra_fields)
        user.save(using=self._db)
        return user
