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
    path('get_game_state/', views.get_game_state, name='get_game_state'),
    path('start_background_loop/', views.start_background_loop, name='start_background_loop'),
    path('stop_background_loop/', views.stop_background_loop, name='stop_background_loop'),
    path('game_start/', views.game_start, name='game_start'), #TODO: needs to work with different numbered games
    path('game_stop/', views.game_stop, name='game_stop'), #TODO: needs to work with different numbered games
    path('left_paddle_up/', views.left_paddle_up, name='left_paddle_up'), #TODO: needs to work with different numbered games
    path('left_paddle_up_release/', views.left_paddle_up_release, name='left_paddle_up_release'), #TODO: needs to work with different numbered games
    path('left_paddle_down/', views.left_paddle_down, name='left_paddle_down'), #TODO: needs to work with different numbered games
    path('left_paddle_down_release/', views.left_paddle_down_release, name='left_paddle_down_release'), #TODO: needs to work with different numbered games
    path('right_paddle_up/', views.right_paddle_up, name='right_paddle_up'), #TODO: needs to work with different numbered games
    path('right_paddle_up_release/', views.right_paddle_up_release, name='right_paddle_up_release'), #TODO: needs to work with different numbered games
    path('right_paddle_down/', views.right_paddle_down, name='right_paddle_down'), #TODO: needs to work with different numbered games
    path('right_paddle_down_release/', views.right_paddle_down_release, name='right_paddle_down_release'), #TODO: needs to work with different numbered games
	path('get_canvas/', views.get_canvas, name='get_canvas'),
]
