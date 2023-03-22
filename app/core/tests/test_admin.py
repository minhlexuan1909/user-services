"""
Tests for the Django admin.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test admin site."""

    def setUp(self):
        """Set up."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="test123", name="Test User"
        )

    def test_users_list(self):
        """Test that users are listed on user page."""

        # get the page containing the list of users
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test that the user edit page works."""

        # get the page containing the user edit form
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        # check if the page is loaded successfully
        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the user create page works."""

        # get the page containing the user create form
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        # check if the page is loaded successfully
        self.assertEqual(res.status_code, 200)
