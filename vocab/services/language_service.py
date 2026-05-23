from vocab.constants import LANGUAGE_ENGLISH, LANGUAGE_RUSSIAN


def get_language(request):
    return request.session.get('language', LANGUAGE_ENGLISH)


def is_russian(language):
    return language == LANGUAGE_RUSSIAN