from django import forms
from .models import Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['russian_word', 'translation', 'difficulty', 'notes']
        labels = {
            'russian_word': 'Russian word',
            'translation': 'Translation',
            'difficulty': 'Difficulty',
            'notes': 'Notes',
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_russian_word(self):
        russian_word = self.cleaned_data['russian_word'].strip()

        if len(russian_word) < 2:
            raise forms.ValidationError(
                'Russian word must contain at least 2 characters.'
            )

        return russian_word

    def clean_translation(self):
        translation = self.cleaned_data['translation'].strip()

        if len(translation) < 2:
            raise forms.ValidationError(
                'Translation must contain at least 2 characters.'
            )

        return translation

    def clean_notes(self):
        notes = self.cleaned_data.get('notes', '').strip()

        if len(notes) > 300:
            raise forms.ValidationError(
                'Notes must be 300 characters or less.'
            )

        return notes