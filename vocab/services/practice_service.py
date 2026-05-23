import random

from django.utils import timezone

from vocab.constants import FILTER_ANY, FILTER_NONE, LANGUAGE_RUSSIAN
from vocab.models import Word


def smart_practice_weight(word):
    weight = 10

    if word.practice_seen_count == 0:
        weight += 35

    weight += word.practice_wrong_count * 10
    weight += word.word_list_open_count * 2
    weight -= word.practice_correct_count * 4

    if word.last_practiced_at:
        days_since_practiced = (timezone.now() - word.last_practiced_at).days
        weight += min(days_since_practiced, 14)
    else:
        weight += 20

    return max(weight, 1)


def smart_sample_words(words, max_questions):
    selected_words = []
    available_words = list(words)

    while available_words and len(selected_words) < max_questions:
        weights = [smart_practice_weight(word) for word in available_words]
        chosen_word = random.choices(available_words, weights=weights, k=1)[0]

        selected_words.append(chosen_word)
        available_words.remove(chosen_word)

    return selected_words


def get_correct_answer(word, language):
    if language == LANGUAGE_RUSSIAN:
        return word.russian_word

    return word.translation


def get_practice_words(user, selected_filter):
    if selected_filter == FILTER_NONE:
        return list(
            Word.objects.filter(
                user=user,
                word_filter__isnull=True,
            )
        ), FILTER_NONE

    if selected_filter == FILTER_ANY:
        return list(Word.objects.filter(user=user)), FILTER_ANY

    return list(
        Word.objects.filter(
            user=user,
            word_filter_id=selected_filter,
        )
    ), selected_filter


def get_available_wrong_words(user, current_word, practice_filter):
    available_wrong_words = list(
        Word.objects.filter(user=user).exclude(id=current_word.id)
    )

    if practice_filter == FILTER_NONE:
        return [
            word for word in available_wrong_words
            if word.word_filter is None
        ]

    if practice_filter not in [FILTER_ANY, None]:
        return [
            word for word in available_wrong_words
            if str(word.word_filter_id) == str(practice_filter)
        ]

    return available_wrong_words


def build_answer_options(current_word, wrong_words, language):
    if language == LANGUAGE_RUSSIAN:
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

    return options


def select_wrong_words(available_wrong_words, used_correct_answers, language):
    if language == LANGUAGE_RUSSIAN:
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
        return random.sample(preferred_wrong_words, 2)

    if len(available_wrong_words) >= 2:
        return random.sample(available_wrong_words, 2)

    return []