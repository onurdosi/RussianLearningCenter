from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from vocab.forms import QuickAddForm, WordForm
from vocab.models import Word, WordFilter
from vocab.services.filter_service import delete_filter_if_empty
from vocab.services.language_service import get_language, is_russian


@login_required
def word_list(request):
    selected_filter = request.GET.get('filter')
    search_query = request.GET.get('search', '').strip()

    words = Word.objects.filter(user=request.user)
    word_filters = WordFilter.objects.filter(user=request.user)

    if search_query:
        words = words.filter(
            Q(russian_word__icontains=search_query) |
            Q(translation__icontains=search_query)
        )

    if selected_filter == 'none':
        words = words.filter(word_filter__isnull=True)
    elif selected_filter:
        words = words.filter(word_filter_id=selected_filter)

    context = {
        'language': get_language(request),
        'words': words,
        'word_filters': word_filters,
        'selected_filter': selected_filter or '',
        'search_query': search_query,
        'result_count': words.count(),
    }

    return render(request, 'pages/word_list.html', context)


@login_required
def add_word(request):
    language = get_language(request)

    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user, language=language)
        if form.is_valid():
            word = form.save()

            if is_russian(language):
                messages.success(request, f'"{word.russian_word}" добавлено в словарь.')
            else:
                messages.success(request, f'"{word.russian_word}" was added to your vocabulary.')

            return redirect('word_list')
    else:
        form = WordForm(user=request.user, language=language)

    title = 'Добавить слово' if is_russian(language) else 'Add Word'

    return render(request, 'pages/word_form.html', {
        'language': language,
        'form': form,
        'title': title,
    })


@login_required
def quick_add_words(request):
    language = get_language(request)

    if request.method == 'POST':
        form = QuickAddForm(request.POST, user=request.user, language=language)
        if form.is_valid():
            russian_words = form.cleaned_data['russian_words_list']
            translations = form.cleaned_data['translations_list']
            word_filter = form.cleaned_data.get('word_filter')
            new_filter_name = form.cleaned_data.get('new_filter_name', '')
            created_new_filter = False

            if new_filter_name:
                word_filter = WordFilter.objects.create(
                    user=request.user,
                    name=new_filter_name,
                )
                created_new_filter = True

            existing_words_normalized = {
                word.russian_word.strip().lower()
                for word in Word.objects.filter(user=request.user)
            }

            words_added_in_this_batch = set()
            added_count = 0
            skipped_count = 0

            for russian_word, translation in zip(russian_words, translations):
                normalized_word = russian_word.strip().lower()

                if (
                    normalized_word in existing_words_normalized or
                    normalized_word in words_added_in_this_batch
                ):
                    skipped_count += 1
                    continue

                Word.objects.create(
                    user=request.user,
                    russian_word=russian_word.strip(),
                    translation=translation.strip(),
                    word_filter=word_filter,
                    notes='',
                )
                words_added_in_this_batch.add(normalized_word)
                added_count += 1

            if created_new_filter and added_count == 0:
                word_filter.delete()

            if added_count > 0:
                messages.success(
                    request,
                    f'{added_count} слов(а) успешно добавлено.'
                    if is_russian(language)
                    else f'{added_count} word(s) added successfully.'
                )

            if skipped_count > 0:
                messages.info(
                    request,
                    f'{skipped_count} повторяющихся слов(а) пропущено.'
                    if is_russian(language)
                    else f'{skipped_count} duplicate word(s) were skipped.'
                )

            return redirect('word_list')
    else:
        form = QuickAddForm(user=request.user, language=language)

    return render(request, 'pages/quick_add.html', {
        'language': language,
        'form': form,
    })


@login_required
def edit_word(request, word_id):
    language = get_language(request)
    word = get_object_or_404(Word, id=word_id, user=request.user)
    old_filter = word.word_filter

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word, user=request.user, language=language)
        if form.is_valid():
            updated_word = form.save()

            if old_filter != updated_word.word_filter:
                delete_filter_if_empty(old_filter)

            messages.success(
                request,
                f'"{updated_word.russian_word}" успешно обновлено.'
                if is_russian(language)
                else f'"{updated_word.russian_word}" was updated successfully.'
            )

            return redirect('word_list')
    else:
        form = WordForm(instance=word, user=request.user, language=language)

    title = 'Редактировать слово' if is_russian(language) else 'Edit Word'

    return render(request, 'pages/word_form.html', {
        'language': language,
        'form': form,
        'title': title,
    })


@login_required
def delete_word(request, word_id):
    language = get_language(request)
    word = get_object_or_404(Word, id=word_id, user=request.user)

    if request.method == 'POST':
        word_name = word.russian_word
        old_filter = word.word_filter
        word.delete()
        delete_filter_if_empty(old_filter)

        messages.success(
            request,
            f'"{word_name}" удалено из словаря.'
            if is_russian(language)
            else f'"{word_name}" was deleted from your vocabulary.'
        )

        return redirect('word_list')

    return render(request, 'pages/delete_word.html', {
        'language': language,
        'word': word,
    })