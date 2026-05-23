from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from vocab.models import Word, WordFilter


class FilterViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_delete_filter_only_keeps_words(self):
        word_filter = WordFilter.objects.create(user=self.user, name='travel')

        word = Word.objects.create(
            user=self.user,
            russian_word='поезд',
            translation='train',
            word_filter=word_filter,
        )

        response = self.client.post(reverse('delete_filter', args=[word_filter.id]))

        self.assertEqual(response.status_code, 302)

        word.refresh_from_db()

        self.assertIsNone(word.word_filter)
        self.assertFalse(WordFilter.objects.filter(id=word_filter.id).exists())

    def test_delete_filter_words_deletes_filter_and_words(self):
        word_filter = WordFilter.objects.create(user=self.user, name='food')

        Word.objects.create(
            user=self.user,
            russian_word='хлеб',
            translation='bread',
            word_filter=word_filter,
        )

        response = self.client.post(reverse('delete_filter_words', args=[word_filter.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Word.objects.filter(russian_word='хлеб').exists())
        self.assertFalse(WordFilter.objects.filter(id=word_filter.id).exists())

    def test_delete_all_words_requires_correct_password(self):
        Word.objects.create(user=self.user, russian_word='дом', translation='house')

        response = self.client.post(reverse('delete_all_words'), {
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Word.objects.filter(user=self.user, russian_word='дом').exists())

    def test_delete_all_words_with_correct_password_deletes_user_words_and_filters(self):
        word_filter = WordFilter.objects.create(user=self.user, name='travel')

        Word.objects.create(
            user=self.user,
            russian_word='поезд',
            translation='train',
            word_filter=word_filter,
        )

        response = self.client.post(reverse('delete_all_words'), {
            'password': 'testpass123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Word.objects.filter(user=self.user).exists())
        self.assertFalse(WordFilter.objects.filter(user=self.user).exists())