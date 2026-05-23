from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import QuickAddForm, WordForm
from .models import Word, WordFilter


class WordFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

    def test_valid_word_form(self):
        form = WordForm(
            data={
                'russian_word': 'привет',
                'translation': 'hello',
                'word_filter': '',
                'new_filter_name': '',
                'notes': 'common greeting',
            },
            user=self.user
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_russian_word_is_not_allowed_for_same_user(self):
        Word.objects.create(
            user=self.user,
            russian_word='привет',
            translation='hello'
        )

        form = WordForm(
            data={
                'russian_word': 'привет',
                'translation': 'hi',
                'word_filter': '',
                'new_filter_name': '',
                'notes': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('russian_word', form.errors)

    def test_same_word_allowed_for_different_users(self):
        Word.objects.create(
            user=self.other_user,
            russian_word='привет',
            translation='hello'
        )

        form = WordForm(
            data={
                'russian_word': 'привет',
                'translation': 'hello',
                'word_filter': '',
                'new_filter_name': '',
                'notes': '',
            },
            user=self.user
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_word_is_case_insensitive_and_trimmed(self):
        Word.objects.create(
            user=self.user,
            russian_word='Привет',
            translation='hello'
        )

        form = WordForm(
            data={
                'russian_word': '  привет  ',
                'translation': 'hi',
                'word_filter': '',
                'new_filter_name': '',
                'notes': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('russian_word', form.errors)

    def test_cannot_choose_filter_and_create_new_filter(self):
        word_filter = WordFilter.objects.create(
            user=self.user,
            name='travel'
        )

        form = WordForm(
            data={
                'russian_word': 'поезд',
                'translation': 'train',
                'word_filter': word_filter.id,
                'new_filter_name': 'food',
                'notes': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())

    def test_duplicate_filter_name_is_not_allowed_case_insensitive(self):
        WordFilter.objects.create(
            user=self.user,
            name='travel'
        )

        form = WordForm(
            data={
                'russian_word': 'поезд',
                'translation': 'train',
                'word_filter': '',
                'new_filter_name': 'Travel',
                'notes': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_filter_name', form.errors)

    def test_new_filter_is_created_when_saving_word(self):
        form = WordForm(
            data={
                'russian_word': 'поезд',
                'translation': 'train',
                'word_filter': '',
                'new_filter_name': 'travel',
                'notes': '',
            },
            user=self.user
        )

        self.assertTrue(form.is_valid())

        word = form.save()

        self.assertEqual(word.user, self.user)
        self.assertIsNotNone(word.word_filter)
        self.assertEqual(word.word_filter.name, 'travel')


class QuickAddFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_valid_quick_add_form(self):
        form = QuickAddForm(
            data={
                'russian_words': 'яблоко, хлеб, молоко',
                'translations': 'apple, bread, milk',
                'word_filter': '',
                'new_filter_name': '',
            },
            user=self.user
        )

        self.assertTrue(form.is_valid())

    def test_quick_add_requires_matching_word_counts(self):
        form = QuickAddForm(
            data={
                'russian_words': 'яблоко, хлеб',
                'translations': 'apple',
                'word_filter': '',
                'new_filter_name': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())

    def test_quick_add_rejects_empty_russian_words(self):
        form = QuickAddForm(
            data={
                'russian_words': '',
                'translations': 'apple, bread',
                'word_filter': '',
                'new_filter_name': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())

    def test_quick_add_rejects_empty_translations(self):
        form = QuickAddForm(
            data={
                'russian_words': 'яблоко, хлеб',
                'translations': '',
                'word_filter': '',
                'new_filter_name': '',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())

    def test_quick_add_cannot_choose_filter_and_create_new_filter(self):
        word_filter = WordFilter.objects.create(
            user=self.user,
            name='food'
        )

        form = QuickAddForm(
            data={
                'russian_words': 'яблоко, хлеб',
                'translations': 'apple, bread',
                'word_filter': word_filter.id,
                'new_filter_name': 'travel',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())

    def test_quick_add_duplicate_filter_name_rejected(self):
        WordFilter.objects.create(
            user=self.user,
            name='food'
        )

        form = QuickAddForm(
            data={
                'russian_words': 'яблоко, хлеб',
                'translations': 'apple, bread',
                'word_filter': '',
                'new_filter_name': 'Food',
            },
            user=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_filter_name', form.errors)


class WordViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client.login(
            username='testuser',
            password='testpass123'
        )

    def test_add_word_creates_word(self):
        response = self.client.post(
            reverse('add_word'),
            {
                'russian_word': 'дом',
                'translation': 'house',
                'word_filter': '',
                'new_filter_name': '',
                'notes': '',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Word.objects.filter(
                user=self.user,
                russian_word='дом'
            ).exists()
        )

    def test_add_word_creates_new_filter(self):
        response = self.client.post(
            reverse('add_word'),
            {
                'russian_word': 'поезд',
                'translation': 'train',
                'word_filter': '',
                'new_filter_name': 'travel',
                'notes': '',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            WordFilter.objects.filter(
                user=self.user,
                name='travel'
            ).exists()
        )
        self.assertTrue(
            Word.objects.filter(
                user=self.user,
                russian_word='поезд',
                word_filter__name='travel'
            ).exists()
        )

    def test_word_list_only_shows_logged_in_users_words(self):
        Word.objects.create(
            user=self.user,
            russian_word='дом',
            translation='house'
        )
        Word.objects.create(
            user=self.other_user,
            russian_word='кот',
            translation='cat'
        )

        response = self.client.get(reverse('word_list'))

        self.assertContains(response, 'дом')
        self.assertNotContains(response, 'кот')

    def test_editing_other_users_word_returns_404(self):
        other_word = Word.objects.create(
            user=self.other_user,
            russian_word='кот',
            translation='cat'
        )

        response = self.client.get(
            reverse('edit_word', args=[other_word.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_filter_only_keeps_words(self):
        word_filter = WordFilter.objects.create(
            user=self.user,
            name='travel'
        )

        word = Word.objects.create(
            user=self.user,
            russian_word='поезд',
            translation='train',
            word_filter=word_filter
        )

        response = self.client.post(
            reverse('delete_filter', args=[word_filter.id])
        )

        self.assertEqual(response.status_code, 302)

        word.refresh_from_db()

        self.assertIsNone(word.word_filter)
        self.assertFalse(
            WordFilter.objects.filter(id=word_filter.id).exists()
        )

    def test_delete_filter_words_deletes_filter_and_words(self):
        word_filter = WordFilter.objects.create(
            user=self.user,
            name='food'
        )

        Word.objects.create(
            user=self.user,
            russian_word='хлеб',
            translation='bread',
            word_filter=word_filter
        )

        response = self.client.post(
            reverse('delete_filter_words', args=[word_filter.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Word.objects.filter(russian_word='хлеб').exists()
        )
        self.assertFalse(
            WordFilter.objects.filter(id=word_filter.id).exists()
        )

    def test_delete_all_words_requires_correct_password(self):
        Word.objects.create(
            user=self.user,
            russian_word='дом',
            translation='house'
        )

        response = self.client.post(
            reverse('delete_all_words'),
            {
                'password': 'wrong-password'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Word.objects.filter(
                user=self.user,
                russian_word='дом'
            ).exists()
        )

    def test_delete_all_words_with_correct_password_deletes_user_words_and_filters(self):
        word_filter = WordFilter.objects.create(
            user=self.user,
            name='travel'
        )

        Word.objects.create(
            user=self.user,
            russian_word='поезд',
            translation='train',
            word_filter=word_filter
        )

        response = self.client.post(
            reverse('delete_all_words'),
            {
                'password': 'testpass123'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Word.objects.filter(user=self.user).exists()
        )
        self.assertFalse(
            WordFilter.objects.filter(user=self.user).exists()
        )


class PracticeModeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(
            username='testuser',
            password='testpass123'
        )

    def test_practice_requires_at_least_three_words(self):
        Word.objects.create(
            user=self.user,
            russian_word='дом',
            translation='house'
        )
        Word.objects.create(
            user=self.user,
            russian_word='кот',
            translation='cat'
        )

        response = self.client.get(
            reverse('practice_word') + '?filter=any'
        )

        self.assertContains(response, 'You need at least 3 words')

    def test_practice_marks_word_as_practiced_once_after_answer(self):
        words = [
            Word.objects.create(
                user=self.user,
                russian_word='дом',
                translation='house'
            ),
            Word.objects.create(
                user=self.user,
                russian_word='кот',
                translation='cat'
            ),
            Word.objects.create(
                user=self.user,
                russian_word='хлеб',
                translation='bread'
            ),
        ]

        self.client.get(reverse('practice_word') + '?filter=any')

        practice_word_ids = self.client.session['practice_word_ids']
        current_word_id = practice_word_ids[0]
        current_word = Word.objects.get(id=current_word_id)

        response = self.client.post(
            reverse('practice_word'),
            {
                'word_id': current_word.id,
                'selected_answer': current_word.translation,
            }
        )

        self.assertEqual(response.status_code, 200)

        current_word.refresh_from_db()

        self.assertTrue(current_word.practiced_once)