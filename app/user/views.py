"""
Views for the user API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


# RetrieveUpdateAPIView: retrieve and update the object
# Retrieve: GET
# Update: PUT, PATCH
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    # Set who can access this view (only authenticated user can access)
    permission_classes = (permissions.IsAuthenticated,)

    # Override the default get_object method (GET request)
    def get_object(self):
        """Retrieve and return authentication user"""
        return self.request.user
