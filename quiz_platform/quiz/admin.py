from django.contrib import admin
from .models import *

admin.site.register(QuizCategory)
admin.site.register(DifficultyLevel)
admin.site.register(Score)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "category")
    list_filter = ("category",)

