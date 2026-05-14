from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='vocab/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    path('', views.home, name='home'),
    path('language/<str:language>/', views.set_language, name='set_language'),
    path('words/', views.word_list, name='word_list'),
    path('add/', views.add_word, name='add_word'),
    path('quick-add/', views.quick_add_words, name='quick_add_words'),
    path('edit/<int:word_id>/', views.edit_word, name='edit_word'),
    path('delete/<int:word_id>/', views.delete_word, name='delete_word'),
    path('practice/', views.practice_word, name='practice_word'),
]