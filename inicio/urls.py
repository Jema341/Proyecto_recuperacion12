from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ui-icons/', views.ui_icons, name='ui_icons'),
    path('forms/', views.forms, name='forms'),
    path('tables/', views.tables, name='tables'),
    path('calendar/', views.calendar, name='calendar'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('registration/', views.registration, name='registration'),
    
]