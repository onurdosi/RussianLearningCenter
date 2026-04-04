from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('words/', views.word_list, name='word_list'),
    path('add/', views.add_word, name='add_word'),
    path('quick-add/', views.quick_add_words, name='quick_add_words'),
    path('edit/<int:word_id>/', views.edit_word, name='edit_word'),
    path('delete/<int:word_id>/', views.delete_word, name='delete_word'),
    path('practice/', views.practice_word, name='practice_word'),
]