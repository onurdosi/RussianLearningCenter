from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from vocab.models import Word
from vocab.services.statistics_service import increment_word_open_count


@login_required
def track_word_open(request, word_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)

    word = get_object_or_404(Word, id=word_id, user=request.user)
    increment_word_open_count(word)

    return JsonResponse({'ok': True})