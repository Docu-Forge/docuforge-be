from django.urls import path
from .views import RegisterView, LoginView, ProfileView, CodeGrantAuthView, CallbackView, UserinfoView

app_name = 'auth'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('code_grant_auth/', CodeGrantAuthView.as_view(), name='code_grant_auth'),
    path('callback/', CallbackView.as_view(), name='callback'),
    path('userinfo/', UserinfoView.as_view(), name='userinfo'),
]
