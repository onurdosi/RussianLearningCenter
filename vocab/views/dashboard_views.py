from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from vocab.models import Word, WordFilter
from vocab.services.language_service import get_language


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

    top_mistake_words = user_words.filter(
        practice_wrong_count__gt=0
    ).order_by('-practice_wrong_count', 'russian_word')[:3]

    recent_mistake_words = user_words.filter(
        last_wrong_at__isnull=False
    ).order_by('-last_wrong_at')[:3]

    most_clicked_word = user_words.filter(
        word_list_open_count__gt=0
    ).order_by('-word_list_open_count', 'russian_word').first()

    context = {
        'language': get_language(request),
        'total_words': total_words,
        'total_filters': total_filters,
        'word_filters': user_filters,
        'has_no_filter_words': user_words.filter(word_filter__isnull=True).exists(),
        'practiced_percentage': practiced_percentage,
        'top_mistake_words': top_mistake_words,
        'recent_mistake_words': recent_mistake_words,
        'most_clicked_word': most_clicked_word,
    }

    return render(request, 'pages/home.html', context)