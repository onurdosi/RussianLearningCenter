from django import forms

from .models import Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['russian_word', 'translation', 'difficulty', 'notes']

    def clean_russian_word(self):
        russian_word = self.cleaned_data['russian_word'].strip()
        normalized_word = russian_word.lower()

        existing_words = Word.objects.exclude(pk=self.instance.pk)

        for word in existing_words:
            if word.russian_word.strip().lower() == normalized_word:
                raise forms.ValidationError(
                    'This Russian word already exists in your library.'
                )

        return russian_word


class QuickAddForm(forms.Form):
    russian_words = forms.CharField(
        label='Russian words',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Example: привет, дом, вода',
        }),
    )
    translations = forms.CharField(
        label='Translations',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Example: hello, house, water',
        }),
    )
    difficulty = forms.ChoiceField(
        choices=Word.DIFFICULTY_CHOICES,
        initial='medium',
        label='Difficulty',
    )

    def clean(self):
        cleaned_data = super().clean()
        russian_words_text = cleaned_data.get('russian_words', '')
        translations_text = cleaned_data.get('translations', '')

        russian_words = [
            word.strip() for word in russian_words_text.split(',')
            if word.strip()
        ]
        translations = [
            translation.strip() for translation in translations_text.split(',')
            if translation.strip()
        ]

        if not russian_words:
            raise forms.ValidationError(
                'Please enter at least one Russian word.'
            )

        if not translations:
            raise forms.ValidationError(
                'Please enter at least one translation.'
            )

        if len(russian_words) != len(translations):
            raise forms.ValidationError(
                'The number of Russian words and translations must match.'
            )

        cleaned_data['russian_words_list'] = russian_words
        cleaned_data['translations_list'] = translations
        return cleaned_data