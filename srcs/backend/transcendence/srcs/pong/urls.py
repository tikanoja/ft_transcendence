"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   	path('send_game_data/', views.save_game_state, name='send_game_data'),
    path('validate_match/', views.validate_match, name='validate_match'),
	path('post_pong_canvas/', views.post_pong_canvas, name='post_pong_canvas'),
	path('post_cw_canvas/', views.post_cw_canvas, name='post_cw_canvas/'),
    path('authenticate_player/', views.authenticate_player, name='authenticate_player'),
	path('cli_dashboard/<str:username>', views.cli_dashboard, name='cli_dashboard'),
	path('notfound/', views.notfound, name="notfound"),
]