from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('exams', ExamViewSet, basename='exam')

urlpatterns = [
    path("api/register", RegisterView.as_view(), name="Register"),
    path("api/SendOTPForEmailVerify", SendOTPForEmailVerify.as_view(), name="SendOTPForEmailVerify"),
    path("api/VerifyOTP", VerifyOTP.as_view(), name="VerifyOTP"),
    path("api/VerifyEmail", VerifyEmail.as_view(), name="VerifyEmail"),
    path("api/", include(router.urls))
]