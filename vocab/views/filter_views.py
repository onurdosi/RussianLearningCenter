from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from vocab.models import Word, WordFilter
from vocab.services.language_service import get_language, is_russian


@login_required
def delete_filter(request, filter_id):
    language = get_language(request)
    word_filter = get_object_or_404(
        WordFilter,
        id=filter_id,
        user=request.user
    )

    if request.method == 'POST':
        filter_name = word_filter.name

        Word.objects.filter(
            user=request.user,
            word_filter=word_filter
        ).update(word_filter=None)

        word_filter.delete()

        if is_russian(language):
            messages.success(
                request,
                f'Фильтр "{filter_name}" удалён. Слова перемещены в "Без фильтра".'
            )
        else:
            messages.success(
                request,
                f'Filter "{filter_name}" was deleted. Words were moved to No Filter.'
            )

        return redirect('word_list')

    word_count = Word.objects.filter(
        user=request.user,
        word_filter=word_filter
    ).count()

    return render(request, 'pages/delete_filter.html', {
        'language': language,
        'word_filter': word_filter,
        'word_count': word_count,
    })


@login_required
def edit_filter(request, filter_id):
    language = get_language(request)
    word_filter = get_object_or_404(
        WordFilter,
        id=filter_id,
        user=request.user
    )

    if request.method == 'POST':
        new_name = request.POST.get('name', '').strip()

        if not new_name:
            messages.error(request, 'Filter name cannot be empty.')
            return redirect('edit_filter', filter_id=filter_id)

        exists = WordFilter.objects.filter(
            user=request.user,
            name__iexact=new_name
        ).exclude(id=filter_id).exists()

        if exists:
            messages.error(request, 'A filter with this name already exists.')
            return redirect('edit_filter', filter_id=filter_id)

        word_filter.name = new_name
        word_filter.save()

        messages.success(request, 'Filter was updated successfully.')
        return redirect('profile')

    return render(request, 'pages/edit_filter.html', {
        'language': language,
        'word_filter': word_filter,
    })


@login_required
def delete_filter_words(request, filter_id):
    language = get_language(request)
    word_filter = get_object_or_404(
        WordFilter,
        id=filter_id,
        user=request.user
    )

    word_count = Word.objects.filter(
        user=request.user,
        word_filter=word_filter
    ).count()

    if request.method == 'POST':
        filter_name = word_filter.name

        Word.objects.filter(
            user=request.user,
            word_filter=word_filter
        ).delete()

        word_filter.delete()

        if is_russian(language):
            messages.success(
                request,
                f'Фильтр "{filter_name}" и {word_count} слов(а) удалены.'
            )
        else:
            messages.success(
                request,
                f'Filter "{filter_name}" and {word_count} word(s) were deleted.'
            )

        return redirect('profile')

    return render(request, 'pages/delete_filter_words.html', {
        'language': language,
        'word_filter': word_filter,
        'word_count': word_count,
    })