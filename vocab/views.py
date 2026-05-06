import random

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuickAddForm, WordForm
from .models import Word


def home(request):
    total_words = Word.objects.count()
    easy_words = Word.objects.filter(difficulty='easy').count()
    medium_words = Word.objects.filter(difficulty='medium').count()
    hard_words_count = Word.objects.filter(difficulty='hard').count()

    context = {
        'total_words': total_words,
        'easy_words': easy_words,
        'medium_words': medium_words,
        'hard_words_count': hard_words_count,
    }

    return render(request, 'vocab/home.html', context)


def word_list(request):
    selected_difficulty = request.GET.get('difficulty')
    search_query = request.GET.get('search', '').strip()

    words = Word.objects.all()

    if search_query:
        words = words.filter(
            Q(russian_word__icontains=search_query) |
            Q(translation__icontains=search_query)
        )

    result_count = words.count()

    selected_words = []
    other_words = words
    selected_count = 0

    if selected_difficulty in ['easy', 'medium', 'hard']:
        selected_words = words.filter(difficulty=selected_difficulty)
        other_words = words.exclude(difficulty=selected_difficulty)
        selected_count = selected_words.count()
    else:
        selected_difficulty = ''

    context = {
        'words': words,
        'selected_words': selected_words,
        'other_words': other_words,
        'selected_difficulty': selected_difficulty,
        'search_query': search_query,
        'result_count': result_count,
        'selected_count': selected_count,
    }

    return render(request, 'vocab/word_list.html', context)


def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save()
            messages.success(
                request,
                f'"{word.russian_word}" was added to your vocabulary.'
            )
            return redirect('word_list')
    else:
        form = WordForm()

    return render(request, 'vocab/word_form.html', {
        'form': form,
        'title': 'Add Word',
    })


def quick_add_words(request):
    if request.method == 'POST':
        form = QuickAddForm(request.POST)
        if form.is_valid():
            russian_words = form.cleaned_data['russian_words_list']
            translations = form.cleaned_data['translations_list']
            difficulty = form.cleaned_data['difficulty']

            existing_words_normalized = {
                word.russian_word.strip().lower() for word in Word.objects.all()
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
                    russian_word=russian_word.strip(),
                    translation=translation.strip(),
                    difficulty=difficulty,
                    notes='',
                )
                words_added_in_this_batch.add(normalized_word)
                added_count += 1

            if added_count > 0:
                messages.success(
                    request,
                    f'{added_count} word(s) added successfully.'
                )

            if skipped_count > 0:
                messages.info(
                    request,
                    f'{skipped_count} duplicate word(s) were skipped.'
                )

            return redirect('word_list')
    else:
        form = QuickAddForm()

    return render(request, 'vocab/quick_add.html', {
        'form': form,
    })


def edit_word(request, word_id):
    word = get_object_or_404(Word, id=word_id)

    if request.method == 'POST':
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            updated_word = form.save()
            messages.success(
                request,
                f'"{updated_word.russian_word}" was updated successfully.'
            )
            return redirect('word_list')
    else:
        form = WordForm(instance=word)

    return render(request, 'vocab/word_form.html', {
        'form': form,
        'title': 'Edit Word',
    })


def delete_word(request, word_id):
    word = get_object_or_404(Word, id=word_id)

    if request.method == 'POST':
        word_name = word.russian_word
        word.delete()
        messages.success(
            request,
            f'"{word_name}" was deleted from your vocabulary.'
        )
        return redirect('word_list')

    return render(request, 'vocab/delete_word.html', {'word': word})


def practice_word(request):
    difficulty = request.GET.get('difficulty')
    restart = request.GET.get('restart')
    max_questions = 10

    def reset_practice_session():
        request.session.pop('practice_word_ids', None)
        request.session.pop('practice_index', None)
        request.session.pop('practice_score', None)
        request.session.pop('practice_difficulty', None)
        request.session.pop('used_correct_answers', None)
        request.session.pop('wrong_word_ids', None)

    if restart:
        reset_practice_session()
        return redirect('practice_word')

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')
        word_id = request.POST.get('word_id')

        try:
            current_word = Word.objects.get(id=word_id)
        except Word.DoesNotExist:
            reset_practice_session()
            return redirect('practice_word')

        practice_word_ids = request.session.get('practice_word_ids', [])
        practice_index = request.session.get('practice_index', 0)
        practice_score = request.session.get('practice_score', 0)
        practice_difficulty = request.session.get('practice_difficulty', 'any')
        used_correct_answers = request.session.get('used_correct_answers', [])
        wrong_word_ids = request.session.get('wrong_word_ids', [])

        if selected_answer == current_word.translation:
            result = 'correct'
            practice_score += 1
            request.session['practice_score'] = practice_score
        else:
            result = 'wrong'
            if current_word.id not in wrong_word_ids:
                wrong_word_ids.append(current_word.id)
            request.session['wrong_word_ids'] = wrong_word_ids

        used_correct_answers.append(current_word.translation)
        request.session['used_correct_answers'] = used_correct_answers
        request.session['practice_index'] = practice_index + 1

        total_words = len(practice_word_ids)

        context = {
            'current_word': current_word,
            'result': result,
            'selected_answer': selected_answer,
            'correct_answer': current_word.translation,
            'not_enough_words': False,
            'practice_complete': False,
            'total_words': total_words,
            'current_number': practice_index + 1,
            'selected_difficulty': practice_difficulty,
        }

        return render(request, 'vocab/practice.html', context)

    if difficulty:
        if difficulty in ['easy', 'medium', 'hard']:
            words = list(Word.objects.filter(difficulty=difficulty))
            selected_difficulty = difficulty
        else:
            words = list(Word.objects.all())
            selected_difficulty = 'any'

        if len(words) < 3:
            return render(request, 'vocab/practice.html', {
                'not_enough_words': True,
                'selected_difficulty': selected_difficulty,
            })

        random.shuffle(words)
        selected_words = words[:max_questions]

        request.session['practice_word_ids'] = [
            word.id for word in selected_words
        ]
        request.session['practice_index'] = 0
        request.session['practice_score'] = 0
        request.session['practice_difficulty'] = selected_difficulty
        request.session['used_correct_answers'] = []
        request.session['wrong_word_ids'] = []

    practice_word_ids = request.session.get('practice_word_ids')
    practice_index = request.session.get('practice_index', 0)
    practice_score = request.session.get('practice_score', 0)
    selected_difficulty = request.session.get('practice_difficulty')
    used_correct_answers = request.session.get('used_correct_answers', [])

    if not practice_word_ids:
        return render(request, 'vocab/practice.html', {
            'choose_difficulty': True,
            'selected_difficulty': 'any',
        })

    total_words = len(practice_word_ids)

    if practice_index >= total_words:
        wrong_word_ids = request.session.get('wrong_word_ids', [])
        wrong_words = Word.objects.filter(id__in=wrong_word_ids)

        return render(request, 'vocab/practice.html', {
            'practice_complete': True,
            'score': practice_score,
            'total_words': total_words,
            'selected_difficulty': selected_difficulty,
            'wrong_words': wrong_words,
        })

    current_word_id = practice_word_ids[practice_index]

    try:
        current_word = Word.objects.get(id=current_word_id)
    except Word.DoesNotExist:
        reset_practice_session()
        return redirect('practice_word')

    available_wrong_words = list(Word.objects.exclude(id=current_word.id))

    if selected_difficulty in ['easy', 'medium', 'hard']:
        available_wrong_words = [
            word for word in available_wrong_words
            if word.difficulty == selected_difficulty
        ]

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
            'not_enough_words': True,
            'selected_difficulty': selected_difficulty,
        })

    options = [
        current_word.translation,
        wrong_words[0].translation,
        wrong_words[1].translation,
    ]
    random.shuffle(options)

    context = {
        'current_word': current_word,
        'options': options,
        'result': None,
        'selected_answer': None,
        'correct_answer': current_word.translation,
        'not_enough_words': False,
        'practice_complete': False,
        'total_words': total_words,
        'current_number': practice_index + 1,
        'selected_difficulty': selected_difficulty,
        'choose_difficulty': False,
    }

    return render(request, 'vocab/practice.html', context)