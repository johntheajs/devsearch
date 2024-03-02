from django.urls import path
from . import views




urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),


    path('', views.profiles, name="profiles"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),
    path('account/', views.userAccount, name='account'),

    path('edit-account/', views.editAccount, name="edit-account"),

    path('create-skill/', views.createSkill, name="create-skill"),
    path('edit-skill/<str:pk>/', views.editSkill, name="edit-skill"),
    path('delete-skill/<str:pk>/', views.deleteSkill, name="delete-skill"),   

    path('inbox/', views.inbox, name="inbox"),
    path('message/<str:pk>/', views.messageRead, name="message"),
    path('send-message/<str:pk>/', views.createMessage, name="send-message"),
]


