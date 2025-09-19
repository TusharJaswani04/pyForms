from django import forms
from django.forms import modelformset_factory, formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import Form, Question, Option, Response, Answer

class FormCreateForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description', 'theme_color', 'custom_color', 'header_image',
                 'collect_email', 'allow_multiple_responses', 'send_email_notifications',
                 'open_date', 'close_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter form title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter form description (optional)'}),
            'theme_color': forms.Select(attrs={'class': 'form-select'}),
            'custom_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'header_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'open_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'close_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'collect_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_multiple_responses': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-8 mb-3'),
                Column('theme_color', css_class='form-group col-md-4 mb-3'),
            ),
            Field('description', css_class='mb-3'),
            Row(
                Column('custom_color', css_class='form-group col-md-6 mb-3'),
                Column('header_image', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h6 class="mt-4 mb-3">Settings</h6>'),
            Row(
                Column(
                    Div(
                        Field('collect_email', template='forms/checkbox_field.html'),
                        css_class='form-check'
                    ),
                    css_class='col-md-4'
                ),
                Column(
                    Div(
                        Field('allow_multiple_responses', template='forms/checkbox_field.html'),
                        css_class='form-check'
                    ),
                    css_class='col-md-4'
                ),
                Column(
                    Div(
                        Field('send_email_notifications', template='forms/checkbox_field.html'),
                        css_class='form-check'
                    ),
                    css_class='col-md-4'
                ),
            ),
            HTML('<h6 class="mt-4 mb-3">Scheduling (Optional)</h6>'),
            Row(
                Column('open_date', css_class='form-group col-md-6 mb-3'),
                Column('close_date', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Create Form', css_class='btn btn-primary mt-3')
        )

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'help_text', 'question_type', 'is_required', 
                 'scale_min', 'scale_max', 'scale_min_label', 'scale_max_label']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter your question'}),
            'help_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Help text (optional)'}),
            'question_type': forms.Select(attrs={'class': 'form-select question-type-select'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'scale_min': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'scale_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
            'scale_min_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Min label'}),
            'scale_max_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Max label'}),
        }

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control option-input', 'placeholder': 'Option text'}),
        }

# Formsets for dynamic question and option creation
QuestionFormSet = modelformset_factory(
    Question, 
    form=QuestionForm, 
    extra=1, 
    can_delete=True,
    can_order=True
)

OptionFormSet = modelformset_factory(
    Option, 
    form=OptionForm, 
    extra=1, 
    can_delete=True,
    can_order=True
)

class ResponseForm(forms.Form):
    respondent_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email (optional)'})
    )
    respondent_name = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name (optional)'})
    )

    def __init__(self, form_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_instance = form_instance
        
        # Add email field if required by form
        if form_instance.collect_email:
            self.fields['respondent_email'].required = True
        
        # Dynamically add fields for each question
        for question in form_instance.questions.all():
            field_name = f'question_{question.id}'
            
            if question.question_type == 'short_text':
                self.fields[field_name] = forms.CharField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            
            elif question.question_type == 'long_text':
                self.fields[field_name] = forms.CharField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
                )
            
            elif question.question_type == 'multiple_choice':
                choices = [(opt.id, opt.text) for opt in question.options.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
                )
            
            elif question.question_type == 'checkboxes':
                choices = [(opt.id, opt.text) for opt in question.options.all()]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
                )
            
            elif question.question_type == 'dropdown':
                choices = [('', '--- Select ---')] + [(opt.id, opt.text) for opt in question.options.all()]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.Select(attrs={'class': 'form-select'})
                )
            
            elif question.question_type == 'linear_scale':
                scale_min = question.scale_min or 1
                scale_max = question.scale_max or 5
                choices = [(i, str(i)) for i in range(scale_min, scale_max + 1)]
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input linear-scale'})
                )
            
            elif question.question_type == 'date':
                self.fields[field_name] = forms.DateField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )
            
            elif question.question_type == 'time':
                self.fields[field_name] = forms.TimeField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
                )
            
            elif question.question_type == 'file_upload':
                self.fields[field_name] = forms.FileField(
                    label=question.text,
                    required=question.is_required,
                    help_text=question.help_text,
                    widget=forms.FileInput(attrs={'class': 'form-control'})
                )

class DarkModeToggleForm(forms.Form):
    dark_mode = forms.BooleanField(required=False)