from django.urls import include, path
from .views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]