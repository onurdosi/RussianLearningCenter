import random

from django.shortcuts import get_object_or_404, redirect, render

from .forms import WordForm
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
    words = list(Word.objects.all())

    if len(words) < 3:
        return render(request, 'vocab/practice.html', {
            'not_enough_words': True,
        })

    current_word = random.choice(words)
    other_words = [word for word in words if word.id != current_word.id]
    wrong_words = random.sample(other_words, 2)

    options = [
        current_word.translation,
        wrong_words[0].translation,
        wrong_words[1].translation,
    ]
    random.shuffle(options)

    result = None
    selected_answer = None

    if request.method == 'POST':
        selected_answer = request.POST.get('selected_answer')

        if selected_answer == current_word.translation:
            result = 'correct'
        else:
            result = 'wrong'

    context = {
        'current_word': current_word,
        'options': options,
        'result': result,
        'selected_answer': selected_answer,
        'correct_answer': current_word.translation,
        'not_enough_words': False,
    }

    return render(request, 'vocab/practice.html', context)