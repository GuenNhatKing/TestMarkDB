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
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True} 
        }

class ExamPaperSerializer(serializers.ModelSerializer):
    class Meta: 
        model = ExamPaper
        fields = '__all__'
        extra_kwargs = {
            'exam': {'read_only': True} 
        }

class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
        fields = '__all__'
        extra_kwargs = {
            'exam_paper': {'read_only': True} 
        }

class ExamineeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Examinee
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True} 
        }

class OTPRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPRequest
        fields = ('request', 'created_at', 'expired_at')

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionRequest
        fields = ('user', 'token', 'action', 'available', 'expired_at')

class OTPVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=24)
    code = serializers.CharField(max_length=4)

class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=24)

class UploadImageForProcessSerializer(serializers.Serializer):
    exam_id = serializers.CharField()
    examinee_id = serializers.CharField()
    image = serializers.ImageField()

class GetImageUrlSerializer(serializers.Serializer):
    image_name = serializers.CharField()

class ExamineeRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamineeRecord
        fields = '__all__'
        extra_kwargs = {
            'exam': {'read_only': True} 
        }
