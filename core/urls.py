from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('about_triprep/', views.about_triprep, name='about_triprep'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tickets/', views.tickets, name='tickets'),
    path('add_ticket/', views.add_ticket, name='add_ticket'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
]
