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
from pong.views import increase_number, decrease_number, get_number, get_game_state

urlpatterns = [
    path('pong/increase_number/', increase_number, name='increase_number'),
    path('pong/decrease_number/', decrease_number, name='decrease_number'),
    path('pong/get_number/', get_number, name='get_number'),
    path('pong/get_game_state/', get_game_state, name='get_game_state'),
]
