from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('update-user/', views.updateProfile, name='update-user'),
    path('logout/', views.logoutUser, name='logout'),

    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),

    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete/<str:pk>/', views.deleteRoom, name='delete'),
    path('delete-message/<str:rmid>/<str:msgid>/', views.deleteMessage, name='delete-message'),

    path('topics/', views.topicsPage, name='topics'),
    path('activity/', views.activityPage, name='recent-activity'),
]