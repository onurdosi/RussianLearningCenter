from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from vocab.models import Word


class PracticeModeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_practice_requires_at_least_three_words(self):
        Word.objects.create(user=self.user, russian_word='дом', translation='house')
        Word.objects.create(user=self.user, russian_word='кот', translation='cat')

        response = self.client.get(reverse('practice_word') + '?filter=any')

        self.assertContains(response, 'You need at least 3 words')

    def test_practice_marks_word_as_practiced_once_after_answer(self):
        Word.objects.create(user=self.user, russian_word='дом', translation='house')
        Word.objects.create(user=self.user, russian_word='кот', translation='cat')
        Word.objects.create(user=self.user, russian_word='хлеб', translation='bread')

        self.client.get(reverse('practice_word') + '?filter=any')

        practice_word_ids = self.client.session['practice_word_ids']
        current_word_id = practice_word_ids[0]
        current_word = Word.objects.get(id=current_word_id)

        response = self.client.post(reverse('practice_word'), {
            'word_id': current_word.id,
            'selected_answer': current_word.translation,
        })

        self.assertEqual(response.status_code, 200)

        current_word.refresh_from_db()

        self.assertTrue(current_word.practiced_once)