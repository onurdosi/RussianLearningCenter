from django import forms

from .models import Word, WordFilter


class WordForm(forms.ModelForm):
    new_filter_name = forms.CharField(
        required=False,
        label='New filter',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional: create a new filter',
        }),
    )

    class Meta:
        model = Word
        fields = [
            'russian_word',
            'translation',
            'word_filter',
            'new_filter_name',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.fields['word_filter'].required = False
        self.fields['word_filter'].label = 'Filter'

        if self.user:
            self.fields['word_filter'].queryset = WordFilter.objects.filter(
                user=self.user
            )
        else:
            self.fields['word_filter'].queryset = WordFilter.objects.none()

    def clean_russian_word(self):
        russian_word = self.cleaned_data['russian_word'].strip()
        normalized_word = russian_word.lower()

        existing_words = Word.objects.exclude(pk=self.instance.pk)

        if self.user:
            existing_words = existing_words.filter(user=self.user)

        for word in existing_words:
            if word.russian_word.strip().lower() == normalized_word:
                raise forms.ValidationError(
                    'This Russian word already exists in your library.'
                )

        return russian_word

    def clean_new_filter_name(self):
        new_filter_name = self.cleaned_data.get('new_filter_name', '').strip()

        if not new_filter_name:
            return ''

        if self.user:
            filter_exists = WordFilter.objects.filter(
                user=self.user,
                name__iexact=new_filter_name,
            ).exists()

            if filter_exists:
                raise forms.ValidationError(
                    'This filter already exists. Please choose it from the list.'
                )

        return new_filter_name

    def clean(self):
        cleaned_data = super().clean()
        word_filter = cleaned_data.get('word_filter')
        new_filter_name = cleaned_data.get('new_filter_name', '')

        if word_filter and new_filter_name:
            raise forms.ValidationError(
                'Choose an existing filter or create a new one, not both.'
            )

        return cleaned_data

    def save(self, commit=True):
        word = super().save(commit=False)
        new_filter_name = self.cleaned_data.get('new_filter_name', '')

        if self.user:
            word.user = self.user

        if new_filter_name and self.user:
            word_filter = WordFilter.objects.create(
                user=self.user,
                name=new_filter_name,
            )
            word.word_filter = word_filter

        if commit:
            word.save()

        return word


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
    word_filter = forms.ModelChoiceField(
        queryset=WordFilter.objects.none(),
        required=False,
        label='Filter',
    )
    new_filter_name = forms.CharField(
        required=False,
        label='New filter',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional: create a new filter for these words',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['word_filter'].queryset = WordFilter.objects.filter(
                user=self.user
            )

    def clean_new_filter_name(self):
        new_filter_name = self.cleaned_data.get('new_filter_name', '').strip()

        if not new_filter_name:
            return ''

        if self.user:
            filter_exists = WordFilter.objects.filter(
                user=self.user,
                name__iexact=new_filter_name,
            ).exists()

            if filter_exists:
                raise forms.ValidationError(
                    'This filter already exists. Please choose it from the list.'
                )

        return new_filter_name

    def clean(self):
        cleaned_data = super().clean()
        russian_words_text = cleaned_data.get('russian_words', '')
        translations_text = cleaned_data.get('translations', '')
        word_filter = cleaned_data.get('word_filter')
        new_filter_name = cleaned_data.get('new_filter_name', '')

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

        if word_filter and new_filter_name:
            raise forms.ValidationError(
                'Choose an existing filter or create a new one, not both.'
            )

        cleaned_data['russian_words_list'] = russian_words
        cleaned_data['translations_list'] = translations
        return cleaned_data