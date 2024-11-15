from django.urls import path
from . import views

urlpatterns = [
    path('api/dashboard/', views.dashboard, name='dashboard'),
    path('download/csv/', views.download_csv, name='download_csv'),
    path('download/excel/', views.download_excel, name='download_excel'),
    path('upload_file/', views.upload_file, name='upload_file'),

]
