import os
import random
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Q
from django.db.models import Sum
from drf_yasg import openapi
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenViewBase
from django.contrib.auth.views import PasswordChangeView

from users.serializers import CustomUserSerializers
from users.serializers import GetCustomUserSerializers
from users.serializers import TokenObtainLifetimeSerializer
from users.serializers import CreateCustomUserSerializers
from users.serializers import UserUpdateSerializers
from users.serializers import ChangePasswordSerializers
from users.serializers import CustomOTPSerializer
from users.serializers import GetCustomOTPSerializer
from users.models import CustomUser, OTP
# from users.utils import send_email
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from users.forms import PasswordChangeForm, PasswordResetForm



class TokenObtainPairView(TokenViewBase):
    """
    Return JWT tokens (access and refresh) for specific user based on username and password.
    """

    serializer_class = TokenObtainLifetimeSerializer



def generate_otp(username, email):
    try:
        user = get_object_or_404(CustomUser, user_name=username)
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp_code=otp_code)

        subject = "Your OTP Code"
        message = f"Your OTP code is: {otp_code}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        send_mail(
            subject,
            message,
            from_email,
            recipient_list
        )

        return Response(
            {"message": "OTP generated and sent successfully."},
            status=status.HTTP_200_OK,
        )
    except CustomUser.DoesNotExist:
        return Response(
            {"message": "User not found."}, status=status.HTTP_404_NOT_FOUND
        )
         
class ApiViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializers
    parser_classes = [MultiPartParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["id", "user_name"]

    def get_serializer(self, *args, **kwargs):
        if self.action == "partial_update":
            serializer_class = UserUpdateSerializers
            return serializer_class(*args, **kwargs, context={"request": self.request})
        else:
            serializer_class = GetCustomUserSerializers
            return serializer_class(*args, **kwargs, context={"request": self.request})

    
    

    @swagger_auto_schema(request_body=CustomUserSerializers)
    def create(self, request):
        password = request.data["password"]
        mutable_data = request.data.copy()

        if 'password' in mutable_data:
            mutable_data.pop('password')

        serializer = CreateCustomUserSerializers(
            data=mutable_data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        username = self.request.data.get("user_name")
        user_mail = self.request.data.get("email")

        keys_to_remove = []
        for key, value in mutable_data.items():
            keys_to_remove.append(key)

        for key in keys_to_remove:
            mutable_data.pop(key)

        mutable_data['password'] = password
        serializers = ChangePasswordSerializers(data=mutable_data)
        serializers.is_valid(raise_exception=True)
        user.set_password(serializers.data.get("password"))
        user.save()
        generate_otp(username, user_mail)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # {"detail": "CustomUser deleted successfully"}
        return Response(
            {"detail": "User deleted successfully"}, status=status.HTTP_202_ACCEPTED
        )
        
        
# class ChangePasswordView(PasswordChangeView):
#     template_name = "registration/change_password.html"
#     form_class = PasswordChangeForm

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.user, data=self.request.POST)
#         if form.is_valid():
#             super(ChangePasswordView, self).post(request, *args, **kwargs)
#             user = form.save()
#             update_session_auth_hash(request, user)
#             return Response({"password_change_status": "success"})
#         return Response({"error": form.errors if form.errors else None})


class VerifyOTP(APIView):
    queryset = OTP.objects.all()
    serializer_class = CustomOTPSerializer
    # authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(request_body=GetCustomOTPSerializer)
    def post(self, request):
        user = request.data.get("user")
        otp_code = request.data.get("otp_code")
        try:
            user = CustomUser.objects.get(id=user)
            otp = OTP.objects.get(user=user, otp_code=otp_code, is_verified=False)
            otp.is_verified = True
            user.is_verified = True
            user.is_active = True
            user.save()
            otp.save()
            return Response({"message": "OTP verified successfully."})
        except (CustomUser.DoesNotExist, OTP.DoesNotExist):
            return Response({"message": "Invalid OTP or user not found."})