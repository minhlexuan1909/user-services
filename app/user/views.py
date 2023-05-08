"""
Views for the user API
"""
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q

from rest_framework import status, generics, authentication, permissions, serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

import random
import math
import os
from twilio.rest import Client

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    PhoneUpdateSerializer,
    GetPhoneOtpSerializer,
    ConfirmPhoneOtpSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        """Validate and authenticate the user"""
        phone = request.data.get("phone")
        password = request.data.get("password")
        email = request.data.get("email")
        # user = get_user_model().objects.get(phone=phone) or get_user_model().objects.get(
        #     email=email
        # )
        try:
            user = get_user_model().objects.get(Q(phone=phone) | Q(email=email))
        except get_user_model().DoesNotExist:
            return Response(
                {
                    "status": 401,
                    "message": "User phone number or email is not registered",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.phone:
            return Response(
                {
                    "status": 401,
                    "message": "User phone number is not provided",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        print("user", user.is_active)
        # No password => User from Google, Facebook, ...
        if not password:
            # This kind of user have unsuable password (line 22 in models.py) => if they have usable password, they are not authenticated
            if user.has_usable_password():
                return Response(
                    {
                        "status": 403,
                        "message": "User phone number is not verified",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            if not user.is_active:
                return Response(
                    {
                        "status": 403,
                        "message": "User phone number is not verified",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            user = authenticate(
                username=phone,
                password=password,
            )
            if not user:
                return Response(
                    {
                        "status": 403,
                        "message": "Wrong username or password",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # serializer = AuthTokenSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.validated_data["user"]
        # Generate Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "status": 200,
                "data": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
        )


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


class ManageAllUserView(generics.ListAPIView):
    """Manage all users"""

    serializer_class = UserSerializer
    # Set who can access this view (only authenticated user can access)
    permission_classes = (permissions.IsAuthenticated,)

    # Override the default get_object method (GET request)
    def get_queryset(self):
        """Retrieve and return authentication user"""
        return get_user_model().objects.all()


def send_sms(user, phone):
    digits = [i for i in range(0, 10)]
    random_str = ""

    ## create a number of any length for now range = 6
    for i in range(6):
        index = math.floor(random.random() * 10)

        random_str += str(digits[index])

    user.verify_phone_otp = random_str
    user.save()

    phone_converted = "+84" + phone[1:]

    TWILIO_ACCOUNT_SID = "ACd2f88bc27251c6edbdf6d0a38b7a7584"
    TWILIO_AUTH_TOKEN = "336cf2995fa426d7523f2eec2bde39a3"
    phone_number = "+19094036208"
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f"Your verification code is {random_str}",
        from_=phone_number,
        to=phone_converted,
    )
    print(message.sid)
    return random_str


class PhoneUpdateView(generics.UpdateAPIView):
    """Update phone number of the authenticated user"""

    serializer_class = PhoneUpdateSerializer

    def update(self, request, *args, **kwargs):
        """Update phone number of the authenticated user"""

        email = request.data.get("email")
        new_phone = request.data.get("phone")

        if get_user_model().objects.filter(phone=new_phone).exists():
            return Response(
                {
                    "message": "Phone number is already in use",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the phone number
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return Response(
                {
                    "message": "Email is not registered",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.phone = new_phone
        user.save()

        return Response(
            {
                "message": "Phone number is updated",
            },
            status=status.HTTP_200_OK,
        )


class GetPhoneOtpView(generics.CreateAPIView):
    serializer_class = GetPhoneOtpSerializer

    def create(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        try:
            user = get_user_model().objects.get(phone=phone)
        except get_user_model().DoesNotExist:
            return Response(
                {
                    "message": "Phone number is not registered",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = send_sms(user, phone)

        return Response(
            {
                "otp": otp,
            },
            status=status.HTTP_200_OK,
        )


class VerifyPhoneOtpView(generics.CreateAPIView):
    serializer_class = ConfirmPhoneOtpSerializer

    def create(self, request):
        phone = request.data.get("phone")
        otp = request.data.get("otp")
        user = get_user_model().objects.get(phone=phone)
        if user.verify_phone_otp == otp:
            user.is_active = True
            user.save()
            return Response(
                {
                    "message": "Phone number is verified",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Wrong OTP",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
