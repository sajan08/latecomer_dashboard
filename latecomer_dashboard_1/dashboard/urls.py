from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/', views.dashboard, name='dashboard'),
    path('download/csv/', views.download_csv, name='download_csv'),
    path('download/excel/', views.download_excel, name='download_excel'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('', views.user_login, name='home'),  

]
