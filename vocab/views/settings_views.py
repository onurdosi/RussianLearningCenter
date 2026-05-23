from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from vocab.constants import SUPPORTED_LANGUAGES
from vocab.models import Word, WordFilter
from vocab.services.language_service import get_language, is_russian
from vocab.services.statistics_service import reset_user_statistics


def set_language(request, language):
    if language in SUPPORTED_LANGUAGES:
        request.session['language'] = language

    next_url = request.GET.get('next') or 'home'
    return redirect(next_url)


@login_required
def delete_all_words(request):
    language = get_language(request)
    word_count = Word.objects.filter(user=request.user).count()
    filter_count = WordFilter.objects.filter(user=request.user).count()

    if request.method == 'POST':
        password = request.POST.get('password', '')

        if not request.user.check_password(password):
            if is_russian(language):
                messages.error(request, 'Неверный пароль.')
            else:
                messages.error(request, 'Incorrect password.')

            return redirect('delete_all_words')

        Word.objects.filter(user=request.user).delete()
        WordFilter.objects.filter(user=request.user).delete()

        if is_russian(language):
            messages.success(
                request,
                f'Все слова ({word_count}) и фильтры ({filter_count}) удалены.'
            )
        else:
            messages.success(
                request,
                f'All words ({word_count}) and filters ({filter_count}) were deleted.'
            )

        return redirect('profile')

    return render(request, 'pages/delete_all_words.html', {
        'language': language,
        'word_count': word_count,
        'filter_count': filter_count,
    })


@login_required
def reset_statistics(request):
    language = get_language(request)

    if request.method == 'POST':
        reset_user_statistics(request.user)

        if is_russian(language):
            messages.success(request, 'Статистика успешно сброшена.')
        else:
            messages.success(request, 'Statistics were reset successfully.')

        return redirect('home')

    return render(request, 'pages/reset_statistics.html', {
        'language': language,
    })