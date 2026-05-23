from vocab.views.auth_views import (
    signup,
    login_view,
    logout_view,
    profile,
)

from vocab.views.dashboard_views import home

from vocab.views.settings_views import (
    set_language,
    delete_all_words,
    reset_statistics,
)

from vocab.views.word_views import (
    word_list,
    add_word,
    quick_add_words,
    edit_word,
    delete_word,
)

from vocab.views.filter_views import (
    delete_filter,
    delete_filter_words,
    edit_filter,
)

from vocab.views.analytics_views import track_word_open

from vocab.views.practice_views import practice_word