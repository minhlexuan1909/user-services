"""
Serializers for the user API View
"""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    class Meta:
        # Model serializer represents
        model = get_user_model()
        # Fields to be used in the request
        fields = (
            "id",
            "email",
            "password",
            "name",
            "address",
            "address_1",
            "address_2",
            "address_3",
            "phone",
        )
        # password is write only, cannot be read, min length is 5 (for validation)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5, "required": False},
            "phone": {"required": False},
        }

    # Override the default create method
    # The default create method is to create a new object with the validated data, so the password is not encrypted
    # Override it with
    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        if "password" not in validated_data:
            validated_data.pop("password", None)
        if "phone" not in validated_data:
            validated_data.pop("phone", None)
        return get_user_model().objects.create_user(**validated_data)

    # Override the default update method (same reason as above)
    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # Retrive the password from the validated data dict (might contains name, password)
        # Pop: get and remove from the dict (password need to be encrypted before saving, other info can be saved directly)
        password = validated_data.pop("password", None)
        # save here
        # super the default update method from Serializer class
        user = super().update(instance, validated_data)

        # if password is contained in the validated data (means that user want to change password), set the password
        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token"""

    phone = serializers.CharField(required=False)
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False, allow_blank=True, required=False
    )
    email = serializers.EmailField(required=False)


class PhoneUpdateSerializer(serializers.Serializer):
    phone = serializers.CharField()
    email = serializers.EmailField(required=False)


class GetPhoneOtpSerializer(serializers.Serializer):
    phone = serializers.CharField()


class ConfirmPhoneOtpSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField(max_length=6)
