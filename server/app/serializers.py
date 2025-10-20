from rest_framework import serializers
from .models import *
from django.db import transaction
from .tasks import upload_image, get_image_url

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
    # input: nhận file từ multipart/form-data
    img_before_process_input = serializers.ImageField(write_only=True, required=False)
    img_after_process_input  = serializers.ImageField(write_only=True, required=False)

    # stored: chuỗi để client thấy được giá trị đã lưu
    img_before_process = serializers.CharField(read_only=True) 
    img_after_process  = serializers.CharField(read_only=True)
    class Meta:
        model = ExamineeRecord
        fields = '__all__'
        extra_kwargs = {
            'exam': {'read_only': True} 
        }
    
    @transaction.atomic
    def create(self, validated_data):
        img_before_file = validated_data.pop("img_before_process_input", None)
        img_after_file  = validated_data.pop("img_after_process_input", None)
        
        if img_before_file:
            validated_data["img_before_process"] = upload_image(file=img_before_file) 
        if img_after_file:
            validated_data["img_after_process"] = upload_image(file=img_after_file) 

        return super().create(validated_data)
    
    @transaction.atomic
    def update(self, instance, validated_data):
        img_before_file = validated_data.pop("img_before_process_input", None)
        img_after_file  = validated_data.pop("img_after_process_input", None)

        if img_before_file:
            instance.img_before_process = upload_image(file=img_before_file)
        if img_after_file:
            instance.img_after_process = upload_image(file=img_after_file)

        return super().update(instance, validated_data)
