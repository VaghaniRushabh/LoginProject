from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import CustomUser, OTP
from users.utils import fcm_update


class CustomUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "user_name",
            "email",
            "phone",
            "password",
        )
        
class CreateCustomUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "user_name",
            "email",
            "phone"
        )




class GetCustomUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "user_name",
            "email",
            "phone",
            "date_joined",
            "is_active",
        )




class ChangePasswordSerializers(serializers.ModelSerializer):
    password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['password']

class TokenObtainLifetimeSerializer(TokenObtainPairSerializer):
    default_error_messages = {"no_active_account": _("Could not find your account")}

    def validate(self, attrs):
        data = super().validate(attrs)
        print("self.user : ", self.user)
        user = GetCustomUserSerializers(self.user, context=self.context).data
        data.update({"user": user})
        return data
    
    
    
class UserUpdateSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "user_name",
            "email",
            "phone",
        )

class CustomOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = "__all__"


class GetCustomOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = (
            "user",
            "otp_code",
        )