"""
Definition of urls for Zabbix_Maintenance.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Вход',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),
    path('get_crq_time/', views.get_crq_time, name='skuf_crq_time'),
    path('create_mm/', views.create_mm, name='create_mm'),
    path('stands/create_stand/', views.create_stand, name='create_stand'),
    path('stands/change_stand/', views.change_stand, name='change_stand'),
    path('stands/delete_stand/', views.delete_stand, name='delete_stand'),
    path('stands/', views.stands, name='stands')
    
]
