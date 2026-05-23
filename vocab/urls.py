from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('', views.home, name='home'),
    path('language/<str:language>/', views.set_language, name='set_language'),
    path('words/', views.word_list, name='word_list'),
    path('words/<int:word_id>/track-open/', views.track_word_open, name='track_word_open'),
    path('add/', views.add_word, name='add_word'),
    path('quick-add/', views.quick_add_words, name='quick_add_words'),
    path('edit/<int:word_id>/', views.edit_word, name='edit_word'),
    path('delete/<int:word_id>/', views.delete_word, name='delete_word'),

    path('delete-filter/<int:filter_id>/', views.delete_filter, name='delete_filter'),
    path(
        'delete-filter-words/<int:filter_id>/',
        views.delete_filter_words,
        name='delete_filter_words'
    ),
    path('delete-all-words/', views.delete_all_words, name='delete_all_words'),
    path('reset-statistics/', views.reset_statistics, name='reset_statistics'),
    path('edit-filter/<int:filter_id>/', views.edit_filter, name='edit_filter'),

    path('practice/', views.practice_word, name='practice_word'),
]