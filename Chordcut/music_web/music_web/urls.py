"""
URL configuration for music_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from music_app.views import *
urlpatterns = [
    path("admin/", admin.site.urls),
    path('', index_page, name='front_page'),  
    path('index_page/', index_page, name='index_page'), 
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path('login_page/', login_page, name='login_page'), 
    path('home_page/', home_page, name='home_page'), 
    path('about_page/', about_page, name='about_page'), 
    path('contact_page/', contact_page, name='contact_page'), 
    path('service_page/', service_page, name='service_page'), 
    path('logout/', logout, name='logout'),
    path('seprate_page/', seprate_page, name='seprate_page'),
    path('separate-audio/', audio_separation_view, name='audio_separation'),
    path('remix_page/', remix_page, name='remix_page'),
    path('audio_remix/', audio_remix, name='audio_remix'),
    path('combaine_page/', combaine_page, name='combaine_page'),
    path('audio_combine/', audio_combine, name='audio_combine'),
    
]
