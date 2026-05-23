from django.db.models import F

from vocab.models import Word


def increment_word_open_count(word):
    Word.objects.filter(id=word.id).update(
        word_list_open_count=F('word_list_open_count') + 1
    )


def reset_user_statistics(user):
    Word.objects.filter(user=user).update(
        practiced_once=False,
        word_list_open_count=0,
        practice_seen_count=0,
        practice_correct_count=0,
        practice_wrong_count=0,
        last_practiced_at=None,
        last_wrong_at=None,
    )