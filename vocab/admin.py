from django.contrib import admin

from .models import Word, WordFilter


admin.site.register(Word)
admin.site.register(WordFilter)