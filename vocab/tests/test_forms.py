from django.contrib.auth.models import User
from django.test import TestCase

from vocab.forms import QuickAddForm, WordForm
from vocab.models import Word, WordFilter


class WordFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')

    def test_valid_word_form(self):
        form = WordForm(data={
            'russian_word': 'привет',
            'translation': 'hello',
            'word_filter': '',
            'new_filter_name': '',
            'notes': 'common greeting',
        }, user=self.user)

        self.assertTrue(form.is_valid())

    def test_duplicate_russian_word_is_not_allowed_for_same_user(self):
        Word.objects.create(user=self.user, russian_word='привет', translation='hello')

        form = WordForm(data={
            'russian_word': 'привет',
            'translation': 'hi',
            'word_filter': '',
            'new_filter_name': '',
            'notes': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('russian_word', form.errors)

    def test_same_word_allowed_for_different_users(self):
        Word.objects.create(user=self.other_user, russian_word='привет', translation='hello')

        form = WordForm(data={
            'russian_word': 'привет',
            'translation': 'hello',
            'word_filter': '',
            'new_filter_name': '',
            'notes': '',
        }, user=self.user)

        self.assertTrue(form.is_valid())

    def test_duplicate_word_is_case_insensitive_and_trimmed(self):
        Word.objects.create(user=self.user, russian_word='Привет', translation='hello')

        form = WordForm(data={
            'russian_word': '  привет  ',
            'translation': 'hi',
            'word_filter': '',
            'new_filter_name': '',
            'notes': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('russian_word', form.errors)

    def test_cannot_choose_filter_and_create_new_filter(self):
        word_filter = WordFilter.objects.create(user=self.user, name='travel')

        form = WordForm(data={
            'russian_word': 'поезд',
            'translation': 'train',
            'word_filter': word_filter.id,
            'new_filter_name': 'food',
            'notes': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())

    def test_duplicate_filter_name_is_not_allowed_case_insensitive(self):
        WordFilter.objects.create(user=self.user, name='travel')

        form = WordForm(data={
            'russian_word': 'поезд',
            'translation': 'train',
            'word_filter': '',
            'new_filter_name': 'Travel',
            'notes': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('new_filter_name', form.errors)

    def test_new_filter_is_created_when_saving_word(self):
        form = WordForm(data={
            'russian_word': 'поезд',
            'translation': 'train',
            'word_filter': '',
            'new_filter_name': 'travel',
            'notes': '',
        }, user=self.user)

        self.assertTrue(form.is_valid())

        word = form.save()

        self.assertEqual(word.user, self.user)
        self.assertIsNotNone(word.word_filter)
        self.assertEqual(word.word_filter.name, 'travel')


class QuickAddFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_valid_quick_add_form(self):
        form = QuickAddForm(data={
            'russian_words': 'яблоко, хлеб, молоко',
            'translations': 'apple, bread, milk',
            'word_filter': '',
            'new_filter_name': '',
        }, user=self.user)

        self.assertTrue(form.is_valid())

    def test_quick_add_requires_matching_word_counts(self):
        form = QuickAddForm(data={
            'russian_words': 'яблоко, хлеб',
            'translations': 'apple',
            'word_filter': '',
            'new_filter_name': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())

    def test_quick_add_rejects_empty_russian_words(self):
        form = QuickAddForm(data={
            'russian_words': '',
            'translations': 'apple, bread',
            'word_filter': '',
            'new_filter_name': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())

    def test_quick_add_rejects_empty_translations(self):
        form = QuickAddForm(data={
            'russian_words': 'яблоко, хлеб',
            'translations': '',
            'word_filter': '',
            'new_filter_name': '',
        }, user=self.user)

        self.assertFalse(form.is_valid())

    def test_quick_add_cannot_choose_filter_and_create_new_filter(self):
        word_filter = WordFilter.objects.create(user=self.user, name='food')

        form = QuickAddForm(data={
            'russian_words': 'яблоко, хлеб',
            'translations': 'apple, bread',
            'word_filter': word_filter.id,
            'new_filter_name': 'travel',
        }, user=self.user)

        self.assertFalse(form.is_valid())

    def test_quick_add_duplicate_filter_name_rejected(self):
        WordFilter.objects.create(user=self.user, name='food')

        form = QuickAddForm(data={
            'russian_words': 'яблоко, хлеб',
            'translations': 'apple, bread',
            'word_filter': '',
            'new_filter_name': 'Food',
        }, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('new_filter_name', form.errors)