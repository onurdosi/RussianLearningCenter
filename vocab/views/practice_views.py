from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from vocab.constants import (
    FILTER_ANY,
    MAX_PRACTICE_QUESTIONS,
    MIN_PRACTICE_WORDS,
)
from vocab.models import Word, WordFilter
from vocab.services.language_service import get_language
from vocab.services.practice_service import (
    build_answer_options,
    get_available_wrong_words,
    get_correct_answer,
    get_practice_words,
    select_wrong_words,
    smart_sample_words,
    update_review_schedule,
)


@login_required
def practice_word(request):
    language = get_language(request)
    selected_filter = request.GET.get('filter')
    restart = request.GET.get('restart')

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

        practice_word_ids = request.session.get('practice_word_ids', [])
        practice_index = request.session.get('practice_index', 0)
        practice_score = request.session.get('practice_score', 0)
        practice_filter = request.session.get('practice_filter', FILTER_ANY)
        used_correct_answers = request.session.get('used_correct_answers', [])
        wrong_word_ids = request.session.get('wrong_word_ids', [])

        correct_answer = get_correct_answer(current_word, language)
        answered_correctly = selected_answer == correct_answer

        current_word.practice_seen_count += 1

        if answered_correctly:
            result = 'correct'
            practice_score += 1
            current_word.practice_correct_count += 1
            request.session['practice_score'] = practice_score
        else:
            result = 'wrong'
            current_word.practice_wrong_count += 1

            if current_word.id not in wrong_word_ids:
                wrong_word_ids.append(current_word.id)

            request.session['wrong_word_ids'] = wrong_word_ids

        update_review_schedule(current_word, answered_correctly)
        current_word.save()

        used_correct_answers.append(correct_answer)
        request.session['used_correct_answers'] = used_correct_answers
        request.session['practice_index'] = practice_index + 1

        return render(request, 'pages/practice.html', {
            'language': language,
            'current_word': current_word,
            'result': result,
            'selected_answer': selected_answer,
            'correct_answer': correct_answer,
            'not_enough_words': False,
            'practice_complete': False,
            'total_words': len(practice_word_ids),
            'current_number': practice_index + 1,
            'selected_filter': practice_filter,
            'word_filters': word_filters,
        })

    if selected_filter:
        words, practice_filter = get_practice_words(
            request.user,
            selected_filter
        )

        if len(words) < MIN_PRACTICE_WORDS:
            return render(request, 'pages/practice.html', {
                'language': language,
                'not_enough_words': True,
                'selected_filter': practice_filter,
                'word_filters': word_filters,
            })

        selected_words = smart_sample_words(
            words,
            MAX_PRACTICE_QUESTIONS
        )

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
        return render(request, 'pages/practice.html', {
            'language': language,
            'choose_filter': True,
            'selected_filter': FILTER_ANY,
            'word_filters': word_filters,
        })

    total_words = len(practice_word_ids)

    if practice_index >= total_words:
        wrong_word_ids = request.session.get('wrong_word_ids', [])

        wrong_words = Word.objects.filter(
            user=request.user,
            id__in=wrong_word_ids
        )

        return render(request, 'pages/practice.html', {
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

    available_wrong_words = get_available_wrong_words(
        request.user,
        current_word,
        practice_filter
    )

    wrong_words = select_wrong_words(
        available_wrong_words,
        used_correct_answers,
        language
    )

    if len(wrong_words) < 2:
        return render(request, 'pages/practice.html', {
            'language': language,
            'not_enough_words': True,
            'selected_filter': practice_filter,
            'word_filters': word_filters,
        })

    options = build_answer_options(
        current_word,
        wrong_words,
        language
    )

    return render(request, 'pages/practice.html', {
        'language': language,
        'current_word': current_word,
        'options': options,
        'result': None,
        'selected_answer': None,
        'correct_answer': get_correct_answer(current_word, language),
        'not_enough_words': False,
        'practice_complete': False,
        'total_words': total_words,
        'current_number': practice_index + 1,
        'selected_filter': practice_filter,
        'choose_filter': False,
        'word_filters': word_filters,
    })