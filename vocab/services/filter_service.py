from vocab.models import Word


def delete_filter_if_empty(word_filter):
    if word_filter and not Word.objects.filter(word_filter=word_filter).exists():
        word_filter.delete()