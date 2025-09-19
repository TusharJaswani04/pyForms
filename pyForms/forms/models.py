from datetime import date
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

QUESTION_TYPES = [
    ('short_text', 'Short Text'),
    ('long_text', 'Paragraph'),
    ('multiple_choice', 'Multiple Choice'),
    ('checkboxes', 'Checkboxes'),
    ('dropdown', 'Dropdown'),
    ('linear_scale', 'Linear Scale'),
    ('multiple_choice_grid', 'Multiple Choice Grid'),
    ('date', 'Date'),
    ('time', 'Time'),
    ('file_upload', 'File Upload'),
]

THEME_CHOICES = [
    ('blue', 'Blue'),
    ('red', 'Red'),
    ('green', 'Green'),
    ('purple', 'Purple'),
    ('orange', 'Orange'),
    ('teal', 'Teal'),
    ('pink', 'Pink'),
    ('indigo', 'Indigo'),
    ('custom', 'Custom'),
]

class Form(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    title = models.CharField(max_length=255, default='Untitled Form')
    description = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    allow_multiple_responses = models.BooleanField(default=True)
    collect_email = models.BooleanField(default=False)
    
    # Scheduling
    open_date = models.DateTimeField(null=True, blank=True)
    close_date = models.DateTimeField(null=True, blank=True)
    
    # Theming
    theme_color = models.CharField(max_length=20, choices=THEME_CHOICES, default='blue')
    custom_color = models.CharField(max_length=7, blank=True, null=True, help_text='Hex color code')
    header_image = models.ImageField(upload_to='form_headers/', blank=True, null=True)
    
    # Email notifications
    send_email_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_open(self):
        now = timezone.now()
        if self.open_date and now < self.open_date:
            return False
        if self.close_date and now > self.close_date:
            return False
        return True
    
    @property
    def response_count(self):
        return self.responses.count()
    
    @property
    def share_url(self):
        return f'/form/{self.uuid}/'

class Question(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    help_text = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # For linear scale questions
    scale_min = models.IntegerField(default=1, null=True, blank=True)
    scale_max = models.IntegerField(default=5, null=True, blank=True)
    scale_min_label = models.CharField(max_length=100, blank=True, null=True)
    scale_max_label = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form.title} - {self.text[:50]}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text

class Response(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='responses')
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Optional user identification
    respondent_email = models.EmailField(blank=True, null=True)
    respondent_name = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Response to {self.form.title} at {self.submitted_at}"

class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    selected_options = models.ManyToManyField(Option, blank=True)
    file_upload = models.FileField(upload_to='answer_files/', blank=True, null=True)
    
    def __str__(self):
        return f"Answer to: {self.question.text[:30]}"
    
    @property
    def display_answer(self):
        if self.selected_options.exists():
            return ', '.join([option.text for option in self.selected_options.all()])
        elif self.file_upload:
            return f"File: {self.file_upload.name}"
        return self.answer_text or 'No answer'


class Change(models.Model):
    change_date = models.DateField(default=date.today, help_text="Date when the change occurred")
    
    class Meta:
        db_table = 'forms_change'
        verbose_name = 'Change'
        verbose_name_plural = 'Changes'
        ordering = ['-change_date']
    
    def __str__(self):
        return f"Change on {self.change_date}"