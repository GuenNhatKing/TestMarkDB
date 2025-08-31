from django.shortcuts import render
from rest_framework import generics
from .models import CustomUser
from .serializers import UserRegisterSerializer

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer