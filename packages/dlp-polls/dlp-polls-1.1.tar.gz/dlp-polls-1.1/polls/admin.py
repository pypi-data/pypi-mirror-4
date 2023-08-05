from polls.models import *
from django.contrib import admin


class PageInline(admin.TabularInline):
    model = Page
    extra = 2


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 2


class ResultCategoryInline(admin.TabularInline):
    model = PollResultCategory
    extra = 2


class AnswerAdmin(admin.ModelAdmin):
    pass


class ResultCategoryAdmin(admin.ModelAdmin):
    pass


class PageAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]


class PollAdmin(admin.ModelAdmin):
    inlines = [PageInline, ResultCategoryInline]

admin.site.register(Answer, AnswerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(PollResultCategory, ResultCategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Poll, PollAdmin)