from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsVerificated
from .models import *
from .serializers import *
from .tasks import *
from app import randomX
from datetime import datetime, timedelta
import time
from django.http import HttpResponse, Http404
from AI.TestMark import No_Le_AI

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

class ExamViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsVerificated]
    serializer_class = ExamSerializer

    def get_queryset(self):
        queryset = Exam.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExamPaperViewSet(viewsets.ModelViewSet):
    serializer_class = ExamPaperSerializer

    def get_queryset(self):
        exam = Exam.objects.get(pk=self.kwargs['exam_pk'])
        return ExamPaper.objects.filter(exam=exam)

    def perform_create(self, serializer):
        exam = Exam.objects.get(pk=self.kwargs['exam_pk'])
        serializer.save(exam=exam)

class ExamAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = ExamAnswerSerializer

    def get_queryset(self):
        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_pk'])
        return ExamAnswer.objects.filter(exam_paper=exam_paper)

    def perform_create(self, serializer):
        exam_paper = ExamPaper.objects.get(pk=self.kwargs['exam_paper_pk'])
        serializer.save(exam_paper=exam_paper)
    
class ExamineeViewSet(viewsets.ModelViewSet):
    serializer_class = ExamineeSerializer

    def get_queryset(self):
        queryset = Examinee.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExamineeRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ExamineeRecordSerializer

    def get_queryset(self):
        exam = Exam.objects.get(pk=self.kwargs['exam_pk'])
        return ExamineeRecord.objects.filter(exam=exam)

    def perform_create(self, serializer):
        exam = Exam.objects.get(pk=self.kwargs['exam_pk'])
        serializer.save(exam=exam)

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
    def post(self, request):
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
    def post(self, request):
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
    
class ImageUrl(APIView):
    def get(self, request):
        serializer = ImageUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_name = serializer.validated_data['image_name']
        url = get_image_url(key=image_name)

        return Response(url, status=status.HTTP_200_OK)

class CameraStream(APIView):
    permission_classes = []
    def get(self, request, id):
        data, ts = get_camera_stream(id)
        if not data:
            raise Http404("Không có ảnh cho ID này")
        resp = HttpResponse(data, content_type="image/jpeg")
        resp["X-Timestamp"] = str(ts or 0)
        return resp
    
    def put(self, request, id):
        serializer = CameraStreamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = serializer.validated_data["image"]
        data = image.read()
        ts = int(time.time())
        update_camera_stream(id, data, ts)
        return Response({"ok": True, "id": id, "timestamp": ts}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        user = request.user
        if not user.check_password(old_password):
            return Response({"detail": "Mật khẩu cũ không đúng"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Đổi mật khẩu thành công"}, status=status.HTTP_200_OK)
    
class ImageProcessView(APIView):
    def post(self, request):
        imageProcessSerializer = ImageProcessSerializer(data=request.data)
        imageProcessSerializer.is_valid(raise_exception=True)

        examineeRecord_id = imageProcessSerializer.validated_data.get('id', None)
        examineeRecord = ExamineeRecord.objects.filter(id=examineeRecord_id).first() if examineeRecord_id else None
        image_name = examineeRecord.img_before_process if examineeRecord else None
        if not image_name:
            return Response({"detail": "Không tìm thấy hình ảnh để xử lý"}, status=status.HTTP_400_BAD_REQUEST)

        download_file(local_name=image_name, key_name=image_name)
        ai = No_Le_AI(str_path_image="./temporary/" + image_name)
        result = ai.process_image()
        remove_file(local_name=image_name)
        return Response(result, status=status.HTTP_200_OK)
        