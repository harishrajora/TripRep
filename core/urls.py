from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('process_ticket_pdf/', views.process_ticket_pdf, name='process_ticket_pdf'),
    path('save_ticket/', views.save_ticket, name='save_ticket'),
    path('view_ticket/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)