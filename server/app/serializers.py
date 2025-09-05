from rest_framework import serializers
from .models import *

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'isVerificated')
    
class ExamSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Exam
        exclude = ('user',) # Get all field exclude 'user'

class OTPRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ('request', 'created_at', 'expired_at')

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('user', 'token', 'action', 'available', 'expired_at')

class OTPVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=24)
    code = serializers.CharField(max_length=4)

class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=24)