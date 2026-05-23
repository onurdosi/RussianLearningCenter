from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from vocab.models import Word, WordFilter


class WordViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_add_word_creates_word(self):
        response = self.client.post(reverse('add_word'), {
            'russian_word': 'дом',
            'translation': 'house',
            'word_filter': '',
            'new_filter_name': '',
            'notes': '',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Word.objects.filter(user=self.user, russian_word='дом').exists())

    def test_add_word_creates_new_filter(self):
        response = self.client.post(reverse('add_word'), {
            'russian_word': 'поезд',
            'translation': 'train',
            'word_filter': '',
            'new_filter_name': 'travel',
            'notes': '',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(WordFilter.objects.filter(user=self.user, name='travel').exists())
        self.assertTrue(
            Word.objects.filter(
                user=self.user,
                russian_word='поезд',
                word_filter__name='travel',
            ).exists()
        )

    def test_word_list_only_shows_logged_in_users_words(self):
        Word.objects.create(user=self.user, russian_word='дом', translation='house')
        Word.objects.create(user=self.other_user, russian_word='кот', translation='cat')

        response = self.client.get(reverse('word_list'))

        self.assertContains(response, 'дом')
        self.assertNotContains(response, 'кот')

    def test_editing_other_users_word_returns_404(self):
        other_word = Word.objects.create(
            user=self.other_user,
            russian_word='кот',
            translation='cat',
        )

        response = self.client.get(reverse('edit_word', args=[other_word.id]))

        self.assertEqual(response.status_code, 404)