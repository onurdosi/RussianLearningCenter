import random

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuickAddForm, WordForm
from .models import Word, WordFilter


def get_language(request):
    return request.session.get('language', 'en')


def delete_filter_if_empty(word_filter):
    if word_filter and not Word.objects.filter(word_filter=word_filter).exists():
        word_filter.delete()


def set_language(request, language):
    if language in ['en', 'ru']:
        request.session['language'] = language

    next_url = request.GET.get('next') or 'home'
    return redirect(next_url)


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

    return render(request, 'vocab/signup.html', {
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

    return render(request, 'vocab/login.html', {
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

            if language == 'ru':
                messages.success(request, 'Пароль успешно изменён.')
            else:
                messages.success(request, 'Your password was changed successfully.')

            return redirect('home')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'vocab/profile.html', {
        'language': language,
        'form': form,
        'word_filters': word_filters,
    })


@login_required
def home(request):
    user_words = Word.objects.filter(user=request.user)
    user_filters = WordFilter.objects.filter(user=request.user)

    total_words = user_words.count()
    total_filters = user_filters.count()
    practiced_words = user_words.filter(practiced_once=True).count()

    if total_words > 0:
        practiced_percentage = round((practiced_words / total_words) * 100)
    else:
        practiced_percentage = 0

    context = {
        'language': get_language(request),
        'total_words': total_words,
        'total_filters': total_filters,
        'word_filters': user_filters,
        'has_no_filter_words': user_words.filter(word_filter__isnull=True).exists(),
        'practiced_percentage': practiced_percentage,
    }

    return render(request, 'vocab/home.html', context)


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

    result_count = words.count()

    context = {
        'language': get_language(request),
        'words': words,
        'word_filters': word_filters,
        'selected_filter': selected_filter or '',
        'search_query': search_query,
        'result_count': result_count,
    }

    return render(request, 'vocab/word_list.html', context)


@login_required
def add_word(request):
    language = get_language(request)

    if request.method == 'POST':
        form = WordForm(request.POST, user=request.user)
        if form.is_valid():
            word = form.save()

            if language == 'ru':
                messages.success(
                    request,
                    f'"{word.russian_word}" добавлено в словарь.'
                )
            else:
                messages.success(
                    request,
                    f'"{word.russian_word}" was added to your vocabulary.'
                )
            return redirect('word_list')
    else:
        form = WordForm(user=request.user)

    title = 'Добавить слово' if language == 'ru' else 'Add Word'

    return render(request, 'vocab/word_form.html', {
        'language': language,
        'form': form,
        'title': title,
    })

@login_required
def quick_add_words(request):
    language = get_language(request)

    if request.method == 'POST':
        form = QuickAddForm(request.POST, user=request.user)
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
                if language == 'ru':
                    messages.success(
                        request,
                        f'{added_count} слов(а) успешно добавлено.'
                    )
                else:
                    messages.success(
                        request,
                        f'{added_count} word(s) added successfully.'
                    )

            if skipped_count > 0:
                if language == 'ru':
                    messages.info(
                        request,
                        f'{skipped_count} повторяющихся слов(а) пропущено.'
                    )
                else:
                    messages.info(
                        request,
                        f'{skipped_count} duplicate word(s) were skipped.'
                    )

            return redirect('word_list')
    else:
        form = QuickAddForm(user=request.user)

    return render(request, 'vocab/quick_add.html', {
        'language': language,
        'form': form,
    })


@login_required
def edit_word(request, word_id):
    language = get_language(request)
    word = get_object_or_404(Word, id=word_id, user=request.user)
    old_filter = word.word_filter

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word, user=request.user)
        if form.is_valid():
            updated_word = form.save()

            if old_filter != updated_word.word_filter:
                delete_filter_if_empty(old_filter)

            if language == 'ru':
                messages.success(
                    request,
                    f'"{updated_word.russian_word}" успешно обновлено.'
                )
            else:
                messages.success(
                    request,
                    f'"{updated_word.russian_word}" was updated successfully.'
                )
            return redirect('word_list')
    else:
        form = WordForm(instance=word, user=request.user)

    title = 'Редактировать слово' if language == 'ru' else 'Edit Word'

    return render(request, 'vocab/word_form.html', {
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
        if language == 'ru':
            messages.success(
                request,
                f'"{word_name}" удалено из словаря.'
            )
        else:
            messages.success(
                request,
                f'"{word_name}" was deleted from your vocabulary.'
            )
        return redirect('word_list')

    return render(request, 'vocab/delete_word.html', {
        'language': language,
        'word': word,
    })


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

        if language == 'ru':
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

    return render(request, 'vocab/delete_filter.html', {
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

    return render(request, 'vocab/edit_filter.html', {
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

        if language == 'ru':
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

    return render(request, 'vocab/delete_filter_words.html', {
        'language': language,
        'word_filter': word_filter,
        'word_count': word_count,
    })


@login_required
def delete_all_words(request):
    language = get_language(request)
    word_count = Word.objects.filter(user=request.user).count()
    filter_count = WordFilter.objects.filter(user=request.user).count()

    if request.method == 'POST':
        password = request.POST.get('password', '')

        if not request.user.check_password(password):
            if language == 'ru':
                messages.error(request, 'Неверный пароль.')
            else:
                messages.error(request, 'Incorrect password.')

            return redirect('delete_all_words')

        Word.objects.filter(user=request.user).delete()
        WordFilter.objects.filter(user=request.user).delete()

        if language == 'ru':
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

    return render(request, 'vocab/delete_all_words.html', {
        'language': language,
        'word_count': word_count,
        'filter_count': filter_count,
    })


@login_required
def practice_word(request):
    language = get_language(request)
    selected_filter = request.GET.get('filter')
    restart = request.GET.get('restart')
    max_questions = 10

    def reset_practice_session():
        request.session.pop('practice_word_ids', None)
        request.session.pop('practice_index', None)
        request.session.pop('practice_score', None)
        request.session.pop('practice_filter', None)
        request.session.pop('used_correct_answers', None)
        request.session.pop('wrong_word_ids', None)

    if restart:
        reset_practice_session()
        return redirect('practice_word')

    word_filters = WordFilter.objects.filter(user=request.user)

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')
        word_id = request.POST.get('word_id')

        try:
            current_word = Word.objects.get(id=word_id, user=request.user)
        except Word.DoesNotExist:
            reset_practice_session()
            return redirect('practice_word')

        current_word.practiced_once = True
        current_word.save()

        practice_word_ids = request.session.get('practice_word_ids', [])
        practice_index = request.session.get('practice_index', 0)
        practice_score = request.session.get('practice_score', 0)
        practice_filter = request.session.get('practice_filter', 'any')
        used_correct_answers = request.session.get('used_correct_answers', [])
        wrong_word_ids = request.session.get('wrong_word_ids', [])

        correct_answer = (
            current_word.russian_word
            if language == 'ru'
            else current_word.translation
        )

        if selected_answer == correct_answer:
            result = 'correct'
            practice_score += 1
            request.session['practice_score'] = practice_score
        else:
            result = 'wrong'
            if current_word.id not in wrong_word_ids:
                wrong_word_ids.append(current_word.id)
            request.session['wrong_word_ids'] = wrong_word_ids

        used_correct_answers.append(correct_answer)
        request.session['used_correct_answers'] = used_correct_answers
        request.session['practice_index'] = practice_index + 1

        total_words = len(practice_word_ids)

        context = {
            'language': language,
            'current_word': current_word,
            'result': result,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer,
            'not_enough_words': False,
            'practice_complete': False,
            'total_words': total_words,
            'current_number': practice_index + 1,
            'selected_filter': practice_filter,
            'word_filters': word_filters,
        }

        return render(request, 'vocab/practice.html', context)

    if selected_filter:
        if selected_filter == 'none':
            words = list(
                Word.objects.filter(
                    user=request.user,
                    word_filter__isnull=True,
                )
            )
            practice_filter = 'none'
        elif selected_filter == 'any':
            words = list(Word.objects.filter(user=request.user))
            practice_filter = 'any'
        else:
            words = list(
                Word.objects.filter(
                    user=request.user,
                    word_filter_id=selected_filter,
                )
            )
            practice_filter = selected_filter

        if len(words) < 3:
            return render(request, 'vocab/practice.html', {
                'language': language,
                'not_enough_words': True,
                'selected_filter': practice_filter,
                'word_filters': word_filters,
            })

        random.shuffle(words)
        selected_words = words[:max_questions]

        request.session['practice_word_ids'] = [
            word.id for word in selected_words
        ]
        request.session['practice_index'] = 0
        request.session['practice_score'] = 0
        request.session['practice_filter'] = practice_filter
        request.session['used_correct_answers'] = []
        request.session['wrong_word_ids'] = []

    practice_word_ids = request.session.get('practice_word_ids')
    practice_index = request.session.get('practice_index', 0)
    practice_score = request.session.get('practice_score', 0)
    practice_filter = request.session.get('practice_filter')
    used_correct_answers = request.session.get('used_correct_answers', [])

    if not practice_word_ids:
        return render(request, 'vocab/practice.html', {
            'language': language,
            'choose_filter': True,
            'selected_filter': 'any',
            'word_filters': word_filters,
        })

    total_words = len(practice_word_ids)

    if practice_index >= total_words:
        wrong_word_ids = request.session.get('wrong_word_ids', [])
        wrong_words = Word.objects.filter(
            user=request.user,
            id__in=wrong_word_ids
        )

        return render(request, 'vocab/practice.html', {
            'language': language,
            'practice_complete': True,
            'score': practice_score,
            'total_words': total_words,
            'selected_filter': practice_filter,
            'wrong_words': wrong_words,
            'word_filters': word_filters,
        })

    current_word_id = practice_word_ids[practice_index]

    try:
        current_word = Word.objects.get(
            id=current_word_id,
            user=request.user
        )
    except Word.DoesNotExist:
        reset_practice_session()
        return redirect('practice_word')

    available_wrong_words = list(
        Word.objects.filter(user=request.user).exclude(id=current_word.id)
    )

    if practice_filter == 'none':
        available_wrong_words = [
            word for word in available_wrong_words
            if word.word_filter is None
        ]
    elif practice_filter not in ['any', None]:
        available_wrong_words = [
            word for word in available_wrong_words
            if str(word.word_filter_id) == str(practice_filter)
        ]

    if language == 'ru':
        preferred_wrong_words = [
            word for word in available_wrong_words
            if word.russian_word not in used_correct_answers
        ]
    else:
        preferred_wrong_words = [
            word for word in available_wrong_words
            if word.translation not in used_correct_answers
        ]

    if len(preferred_wrong_words) >= 2:
        wrong_words = random.sample(preferred_wrong_words, 2)
    elif len(available_wrong_words) >= 2:
        wrong_words = random.sample(available_wrong_words, 2)
    else:
        return render(request, 'vocab/practice.html', {
            'language': language,
            'not_enough_words': True,
            'selected_filter': practice_filter,
            'word_filters': word_filters,
        })

    if language == 'ru':
        options = [
            current_word.russian_word,
            wrong_words[0].russian_word,
            wrong_words[1].russian_word,
        ]
    else:
        options = [
            current_word.translation,
            wrong_words[0].translation,
            wrong_words[1].translation,
        ]

    random.shuffle(options)

    context = {
        'language': language,
        'current_word': current_word,
        'options': options,
        'result': None,
        'selected_answer': None,
        'correct_answer': (
            current_word.russian_word
            if language == 'ru'
            else current_word.translation
        ),
        'not_enough_words': False,
        'practice_complete': False,
        'total_words': total_words,
        'current_number': practice_index + 1,
        'selected_filter': practice_filter,
        'choose_filter': False,
        'word_filters': word_filters,
    }

    return render(request, 'vocab/practice.html', context)