from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('Exams', ExamViewSet, basename='Exam')
router.register('Examinees', ExamineeViewSet, basename='Examinee')
router.register('ExamineeRecords', ExamineeRecordViewSet, basename='ExamineeRecord')

urlpatterns = [
    path("api/Register", RegisterView.as_view(), name="Register"),
    
    path("api/SendOTPForEmailVerify", SendOTPForEmailVerify.as_view(), name="SendOTPForEmailVerify"),
    path("api/VerifyOTP", VerifyOTP.as_view(), name="VerifyOTP"),
    path("api/VerifyEmail", VerifyEmail.as_view(), name="VerifyEmail"),
    
    path("api/UploadImageForProcess", UploadImageForProcess.as_view(), name="UploadImageForProcess"),
    path("api/GetImageUrl", GetImageUrl.as_view(), name="GetImageUrl"),
    
    path("api/", include(router.urls))
]