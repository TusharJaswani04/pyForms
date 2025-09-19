from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Form, Question, Option, Response, Answer,Change

class OptionInline(admin.TabularInline):
    model = Option
    extra = 0
    fields = ('text', 'order')

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ('text', 'question_type', 'is_required', 'order')
    readonly_fields = ('created_at',)

@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_published', 'response_count', 'created_at')
    list_filter = ('is_published', 'theme_color', 'created_at')
    search_fields = ('title', 'description', 'user__username', 'user__email')
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'response_count')
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'user', 'title', 'description', 'is_published')
        }),
        ('Settings', {
            'fields': ('allow_multiple_responses', 'collect_email', 'send_email_notifications')
        }),
        ('Scheduling', {
            'fields': ('open_date', 'close_date'),
            'classes': ('collapse',)
        }),
        ('Theming', {
            'fields': ('theme_color', 'custom_color', 'header_image'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_preview', 'form', 'question_type', 'is_required', 'order')
    list_filter = ('question_type', 'is_required', 'created_at')
    search_fields = ('text', 'help_text', 'form__title')
    list_editable = ('order',)
    inlines = [OptionInline]
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('form', 'respondent_name', 'respondent_email', 'submitted_at', 'ip_address')
    list_filter = ('submitted_at', 'form')
    search_fields = ('respondent_name', 'respondent_email', 'form__title')
    readonly_fields = ('submitted_at', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('Response Information', {
            'fields': ('form', 'respondent_name', 'respondent_email')
        }),
        ('Technical Details', {
            'fields': ('submitted_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question_preview', 'display_answer', 'response_date')
    list_filter = ('response__submitted_at', 'question__question_type')
    search_fields = ('answer_text', 'question__text', 'response__respondent_name')
    
    def question_preview(self, obj):
        return obj.question.text[:30] + '...' if len(obj.question.text) > 30 else obj.question.text
    question_preview.short_description = 'Question'
    
    def response_date(self, obj):
        return obj.response.submitted_at
    response_date.short_description = 'Response Date'
    
@admin.register(Change)
class ChangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'change_date')
    list_filter = ('change_date',)
    date_hierarchy = 'change_date'
    ordering = ('-change_date',)

# Customize admin site header
admin.site.site_header = 'pyForms Administration'
admin.site.site_title = 'pyForms Admin'
admin.site.index_title = 'Welcome to pyForms Administration'


