from django.urls import path
from  . import views, play
from .user import relations

urlpatterns = [
	path('register/', views.register_user, name="register_user"),
	path('login/', views.login_user, name="login"),
	path('logout/', views.logout_user, name="logout_user"),
	path('get_current_username/', views.get_current_username, name="get_current_username"),
	path('check_login/', views.check_login, name="check_login"),
	path('profile/<str:username>', views.profile, name="profile"),
	path('friends/', views.friends, name="friends"),
	path('play/', views.play, name="play"),
	path('notfound/', views.notfound, name="notfound"),
	path('manage_account/', views.manage_account, name="manage_account"),
	path('block_user/', relations.block_user, name="block_user"),
	path('tournament_forms/', play.tournament_forms, name='tournament_forms'),
	path('tournament_buttons/', play.tournament_buttons, name='tournament_buttons'),
	path('profile_picture/', views.profile_picture, name="profile_picture"),
]
