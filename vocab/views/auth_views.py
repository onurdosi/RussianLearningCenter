from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.shortcuts import redirect, render

from vocab.models import WordFilter
from vocab.services.language_service import get_language, is_russian


def signup(request):
    language = get_language(request)

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'pages/signup.html', {
        'language': language,
        'form': form,
    })


def login_view(request):
    language = get_language(request)

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'pages/login.html', {
        'language': language,
        'form': form,
    })


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    language = get_language(request)
    word_filters = WordFilter.objects.filter(user=request.user)

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            if is_russian(language):
                messages.success(request, 'Пароль успешно изменён.')
            else:
                messages.success(request, 'Your password was changed successfully.')

            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'pages/profile.html', {
        'language': language,
        'form': form,
        'word_filters': word_filters,
    })