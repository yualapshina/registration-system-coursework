from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dispatcher/', views.dispatcher, name='dispatcher'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('forgot/', views.forgot, name='forgot'),
    path('signout/', views.signout, name='signout'),
    path('profile/', views.profile, name='profile'),
    path('mylist/', views.mylist, name='mylist'),
    path('register/', views.register, name='register'),
    path('timetable/', views.timetable, name='timetable'),
    path('completed/', views.completed, name='completed'),
    path('download/', views.download, name='download'),
    path('feedback/', views.feedback, name='feedback'),
    path('feedback/anonimous', views.feedback_anon, name='feedback_anon'),
    path('certificate/', views.certificate, name='certificate'),
    path('qr/generate/', views.qr_generate, name='qr_generate'),
    path('qr/read/', views.qr_read, name='qr_read'),
    path('errors', views.errors, name='errors'),
]