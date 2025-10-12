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

class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
        fields = '__all__'

class ExamineeSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Examinee
        fields = '__all__'

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
