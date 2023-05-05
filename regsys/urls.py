from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('timetable/', views.timetable, name='timetable'),
    path('completed/', views.completed, name='completed'),
    path('download/', views.download, name='download'),
]