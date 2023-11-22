from django.urls import path

from . import views

urlpatterns = [
    path('dispatcher/', views.dispatcher, name='dispatcher'),
    path('signup/', views.signup, name='signup'),
    path('signup/personal', views.personal, name='personal'),
    path('signin/', views.signin, name='signin'),
    path('profile/', views.profile, name='profile'),
    path('mylist/', views.mylist, name='mylist'),
    path('register/', views.register, name='register'),
    path('timetable/', views.timetable, name='timetable'),
    path('completed/', views.completed, name='completed'),
    path('download/', views.download, name='download'),
    path('feedback/', views.feedback, name='feedback'),
]