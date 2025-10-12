from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsVerificated
from .models import *
from .serializers import *
from .tasks import send_otp, upload_image, get_image_url
from app import randomX
from datetime import datetime, timedelta

# Create your views here.
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class ExamViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsVerificated]
    serializer_class = ExamSerializer

    def get_queryset(self):
        queryset = Exam.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)
    
class ExamAnswerViewSet(viewsets.ModelViewSet):
    queryset = ExamAnswer.objects.all()
    serializer_class = ExamAnswerSerializer

class ExamineeViewSet(viewsets.ModelViewSet):
    queryset = Examinee.objects.all()
    serializer_class = ExamineeSerializer

class ExamineeListViewSet(viewsets.ModelViewSet):
    queryset = ExamineeRecord.objects.all()
    serializer_class = ExamineeRecordSerializer

class SendOTPForEmailVerify(APIView):
    def post(self, request):
        action_request = ActionRequest.objects.filter(
            user = request.user,
            available = False,
            expired_at__gt = datetime.now(),
            action='email_verify'
        ).first()

        if action_request is None:
            token = ''.join(map(str, [randomX.base62[x] for x in randomX.randomX(24, 0, 62)]))
            action_request = ActionRequest(user=request.user, token=token, action='email_verify', expired_at=datetime.now() + timedelta(minutes=5), available=False)
            action_request.save()

        otp_code = randomX.randomOTP()
        otp_request = OTPRequest(code=otp_code, request=action_request, created_at=datetime.now(), expired_at=datetime.now() + timedelta(minutes=5))
        otp_request.save()

        serializer = OTPRequestSerializer(otp_request)

        send_otp.delay_on_commit(action_request.user.email, otp_code)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class VerifyOTP(APIView):
    def patch(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        token = serializer.validated_data['token']

        action_request = ActionRequest.objects.filter(token=token, available=False, expired_at__gt = datetime.now()).first()
        if action_request is None:
            return Response({"detail": "Token không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
        
        otp_request = OTPRequest.objects.filter(
            request=action_request,
            code = code,
            expired_at__gt = datetime.now()
        ).first()

        if otp_request is None:
            return Response({"detail": "OTP không hợp lệ hoặc đã hết hạn"}, status=status.HTTP_400_BAD_REQUEST)

        action_request.available = True
        action_request.save()
        serializer = RequestSerializer(action_request)

        otp_request.delete()

        return Response(serializer.data, status=status.HTTP_200_OK)

class VerifyEmail(APIView):
    def patch(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']

        action_request = ActionRequest.objects.filter(token=token, available=True, expired_at__gt = datetime.now()).first()
        if action_request is None:
            return Response({"detail": "Token không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.filter(username=action_request.user.username).first()
        user.isVerificated = True
        user.save()
        action_request.delete()
        return Response({"detail": "Xác thực email thành công"}, status=status.HTTP_200_OK)

class UploadImageForProcess(APIView):
    def post(self, request):
        serializer = UploadImageForProcessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exam_id = serializer.validated_data['exam_id']
        examinee_id = serializer.validated_data['examinee_id']
        image = serializer.validated_data['image']

        examinee_record = ExamineeList(exam_id=exam_id, examinee_id=examinee_id)
        file_name = upload_image(file=image)
        examinee_record.score = 0 # TODO: score -> nullable
        examinee_record.img_before_process = file_name
        examinee_record.save()

        return Response(file_name, status=status.HTTP_200_OK)
    
class GetImageUrl(APIView):
    def get(self, request):
        serializer = GetImageUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_name = serializer.validated_data['image_name']
        url = get_image_url(key=image_name)

        return Response(url, status=status.HTTP_200_OK)