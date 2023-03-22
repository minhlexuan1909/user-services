"""
Test for models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

# from recipe import models


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successfully(self):
        """Test creating a new user with an email is successful."""
        """example.com is a reserved domain for testing purposes."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""

        """sample_emails is a list of lists. Each list contains two strings. The first string is the email address that we want to test. The second string is the expected normalized version of the email address."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "test123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user with an email raises ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser("test@example.com", "test123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # def test_create_recipe(self):
    #     """Test creating a recipe."""
    #     user = get_user_model().objects.create_user(email="test@example.com", password="test123")

    #     recipe = models.Recipe.objects.create(
    #         user=user,
    #         title="Steak and mushroom sauce",
    #         time_minutes=5,
    #         price=5.00,
    #     )
