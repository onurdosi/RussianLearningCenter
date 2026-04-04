import random

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

    if selected_difficulty in ['easy', 'medium', 'hard']:
        words = Word.objects.filter(difficulty=selected_difficulty)
    else:
        words = Word.objects.all()
        selected_difficulty = ''

    context = {
        'words': words,
        'selected_difficulty': selected_difficulty,
    }

    return render(request, 'vocab/word_list.html', context)


def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            form.save()
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

            for russian_word, translation in zip(russian_words, translations):
                normalized_word = russian_word.strip().lower()

                if (
                    normalized_word in existing_words_normalized or
                    normalized_word in words_added_in_this_batch
                ):
                    continue

                Word.objects.create(
                    russian_word=russian_word.strip(),
                    translation=translation.strip(),
                    difficulty=difficulty,
                    notes='',
                )
                words_added_in_this_batch.add(normalized_word)

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
            form.save()
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
        word.delete()
        return redirect('word_list')

    return render(request, 'vocab/delete_word.html', {'word': word})


def practice_word(request):
    difficulty = request.GET.get('difficulty')
    restart = request.GET.get('restart')

    if restart:
        request.session.pop('practice_word_ids', None)
        request.session.pop('practice_index', None)
        request.session.pop('practice_score', None)
        request.session.pop('practice_difficulty', None)
        return redirect('practice_word')

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')
        word_id = request.POST.get('word_id')

        current_word = get_object_or_404(Word, id=word_id)
        practice_word_ids = request.session.get('practice_word_ids', [])
        practice_index = request.session.get('practice_index', 0)
        practice_score = request.session.get('practice_score', 0)
        practice_difficulty = request.session.get('practice_difficulty', 'any')

        if selected_answer == current_word.translation:
            result = 'correct'
            practice_score += 1
            request.session['practice_score'] = practice_score
        else:
            result = 'wrong'

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
        request.session['practice_word_ids'] = [word.id for word in words]
        request.session['practice_index'] = 0
        request.session['practice_score'] = 0
        request.session['practice_difficulty'] = selected_difficulty

    practice_word_ids = request.session.get('practice_word_ids')
    practice_index = request.session.get('practice_index', 0)
    practice_score = request.session.get('practice_score', 0)
    selected_difficulty = request.session.get('practice_difficulty')

    if not practice_word_ids:
        return render(request, 'vocab/practice.html', {
            'choose_difficulty': True,
            'selected_difficulty': 'any',
        })

    total_words = len(practice_word_ids)

    if practice_index >= total_words:
        return render(request, 'vocab/practice.html', {
            'practice_complete': True,
            'score': practice_score,
            'total_words': total_words,
            'selected_difficulty': selected_difficulty,
        })

    current_word_id = practice_word_ids[practice_index]
    current_word = get_object_or_404(Word, id=current_word_id)

    available_wrong_words = list(
        Word.objects.exclude(id=current_word.id)
    )

    if selected_difficulty in ['easy', 'medium', 'hard']:
        available_wrong_words = [
            word for word in available_wrong_words
            if word.difficulty == selected_difficulty
        ]

    if len(available_wrong_words) < 2:
        return render(request, 'vocab/practice.html', {
            'not_enough_words': True,
            'selected_difficulty': selected_difficulty,
        })

    wrong_words = random.sample(available_wrong_words, 2)

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