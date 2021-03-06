"""Moviemate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from webapp.views import watch, login, index
from webapp.party import party
from webapp.user import api_login, api_login_callback

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/party', party),
    path('api/login', api_login),
    path('api/login_callback', api_login_callback),
    path('watch', watch),
    path('login', login),
    path('home', index),
]
