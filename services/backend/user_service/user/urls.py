from django.urls import path
from  . import views

urlpatterns = [
	path('register/', views.register_user, name="register_user"),
	path('login/', views.login_user, name="login"),
	path('logout/', views.logout_user, name="logout_user"),
	path('get_current_username/', views.get_current_username, name="get_current_username"),
	path('<username:str>/delete-account', views.delete_account, name="delete_account"),
]
