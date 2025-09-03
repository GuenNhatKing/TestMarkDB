from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsVerificated
from .models import *
from .serializers import *
from .tasks import send_otp

# Create your views here.
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class ExamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsVerificated]
    serializer_class = ExamSerializer

    def get_queryset(self):
        queryset = Exam.objects.filter(user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return super().perform_create(serializer)
    
class EmailVerify(APIView):
    def get(self, request):
        send_otp.delay(request.user.email)
        return Response('Đã gửi otp')