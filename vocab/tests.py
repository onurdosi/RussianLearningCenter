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

    def test_duplicate_russian_word_is_not_allowed(self):
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

    def test_duplicate_filter_name_is_not_allowed(self):
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


class WordViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
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