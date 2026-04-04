from django.db import models


class Word(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    russian_word = models.CharField(max_length=100)
    translation = models.CharField(max_length=100)
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.russian_word
