from django.urls import path
from  . import views

urlpatterns = [
	path('register_user/', views.register_user, name="register_user"),
	path('register/', views.register, name='register'),
	path('login_user/', views.login_user, name="login_user"),
	path('logout_user/', views.logout_user, name="logout_user"),
	path('get_current_username/', views.get_current_username, name="get_current_username"),
	path('login/', views.login_user, name="login"),
]
