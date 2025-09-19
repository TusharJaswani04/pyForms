from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, ButtonHolder, HTML
from crispy_forms.bootstrap import FormActions
from datetime import date
import json
from .models import Form, Question, Option, Response, Answer, Change

try:
    from accounts.models import UserProfile
except ImportError:
    UserProfile = None

# FIXED Form for creating new forms with working submit button
class FormCreateForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description', 'collect_email', 'allow_multiple_responses', 'send_email_notifications', 'theme_color']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': 'Form Title',
            'description': 'Form Description',
            'collect_email': 'Collect respondent email addresses',
            'allow_multiple_responses': 'Allow multiple responses from same user',
            'send_email_notifications': 'Send email notifications for new responses',
            'theme_color': 'Theme Color',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make title required
        self.fields['title'].required = True
        self.fields['title'].widget.attrs.update({
            'placeholder': 'Enter your form title',
            'class': 'form-control'
        })
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Describe what this form is for (optional)',
            'class': 'form-control'
        })
        
        # Set up Crispy Forms helper - CRITICAL FOR WORKING SUBMIT
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        
        # Layout with working submit button
        self.helper.layout = Layout(
            'title',
            'description',
            'collect_email',
            'allow_multiple_responses',
            'send_email_notifications',
            'theme_color',
            FormActions(
                Submit('submit', 'Create Form', css_class='btn btn-primary btn-lg'),
                HTML('<a href="{% url \'dashboard\' %}" class="btn btn-outline-secondary ms-2">Cancel</a>')
            )
        )

@login_required
def dashboard(request):
    """User dashboard showing all forms"""
    user_forms = (
        Form.objects
        .filter(user=request.user)
        .annotate(num_responses=Count('responses'))
        .order_by('-created_at')
    )

    # Pagination
    paginator = Paginator(user_forms, 12)
    page_number = request.GET.get('page')
    forms = paginator.get_page(page_number)
    
    # Statistics
    total_forms = user_forms.count()
    total_responses = sum(form.num_responses for form in user_forms)
    published_forms = user_forms.filter(is_published=True).count()
    
    context = {
        'forms': forms,
        'total_forms': total_forms,
        'total_responses': total_responses,
        'published_forms': published_forms,
    }
    return render(request, 'forms/dashboard.html', context)

@login_required
def create_form(request):
    """Create a new form - FIXED VERSION WITH DEBUG"""
    if request.method == 'POST':
        print("POST request received")  # Debug
        print("POST data:", request.POST)  # Debug
        
        form = FormCreateForm(request.POST)
        if form.is_valid():
            print("Form is valid - creating form")  # Debug
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            print(f"Form saved with UUID: {new_form.uuid}")  # Debug
            print(f"Form title: {new_form.title}")  # Debug
            messages.success(request, f'Form "{new_form.title}" created successfully!')
            return redirect('edit_form', form_uuid=new_form.uuid)
        else:
            print("Form is NOT valid")  # Debug
            print("Form errors:", form.errors)  # Debug
            messages.error(request, 'Please correct the errors below.')
    else:
        print("GET request - showing empty form")  # Debug
        form = FormCreateForm()
    
    return render(request, 'forms/create_form.html', {'form': form})

@login_required
def edit_form(request, form_uuid):
    """Edit form and manage questions"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    questions = form_obj.questions.all().order_by('order')
    
    context = {
        'form': form_obj,
        'questions': questions,
    }
    return render(request, 'forms/edit_form.html', context)

@login_required
@require_http_methods(["POST"])
def update_form_settings(request, form_uuid):
    """Update form settings via AJAX"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Update form settings
        if 'title' in data:
            form_obj.title = data['title']
        if 'description' in data:
            form_obj.description = data['description']
        if 'collect_email' in data:
            form_obj.collect_email = str(data['collect_email']).lower() == 'true'
        if 'allow_multiple_responses' in data:
            form_obj.allow_multiple_responses = str(data['allow_multiple_responses']).lower() == 'true'
        if 'send_email_notifications' in data:
            form_obj.send_email_notifications = str(data['send_email_notifications']).lower() == 'true'
        
        form_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Settings updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def add_question(request, form_uuid):
    """Add a new question to the form via AJAX"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    
    try:
        data = json.loads(request.body)
        
        # Get the next order number
        last_question = form_obj.questions.order_by('-order').first()
        next_order = (last_question.order + 1) if last_question else 1
        
        question = Question.objects.create(
            form=form_obj,
            text=data.get('text', 'Untitled Question'),
            question_type=data.get('question_type', 'short_text'),
            is_required=data.get('is_required', True),
            help_text=data.get('help_text', ''),
            order=next_order,
            scale_min=data.get('scale_min'),
            scale_max=data.get('scale_max'),
            scale_min_label=data.get('scale_min_label'),
            scale_max_label=data.get('scale_max_label'),
        )

        # Add options for multiple choice questions
        if data.get('options'):
            for i, option_text in enumerate(data['options']):
                if option_text.strip():  # Only create non-empty options
                    Option.objects.create(
                        question=question,
                        text=option_text.strip(),
                        order=i
                    )

        return JsonResponse({
            'success': True,
            'question_id': question.id,
            'message': 'Question added successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST", "PUT"])
def update_question(request, question_id):
    """Update a question via AJAX"""
    question = get_object_or_404(Question, id=question_id, form__user=request.user)
    
    try:
        data = json.loads(request.body)
        
        question.text = data.get('text', question.text)
        question.question_type = data.get('question_type', question.question_type)
        question.is_required = data.get('is_required', question.is_required)
        question.help_text = data.get('help_text', question.help_text)
        question.scale_min = data.get('scale_min', question.scale_min)
        question.scale_max = data.get('scale_max', question.scale_max)
        question.scale_min_label = data.get('scale_min_label', question.scale_min_label)
        question.scale_max_label = data.get('scale_max_label', question.scale_max_label)
        question.save()

        # Update options if provided
        if 'options' in data:
            question.options.all().delete()
            for i, option_text in enumerate(data['options']):
                if option_text.strip():  # Only create non-empty options
                    Option.objects.create(
                        question=question,
                        text=option_text.strip(),
                        order=i
                    )

        return JsonResponse({
            'success': True,
            'message': 'Question updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_question(request, question_id):
    """Delete a question via AJAX"""
    question = get_object_or_404(Question, id=question_id, form__user=request.user)
    
    try:
        question.delete()
        return JsonResponse({
            'success': True,
            'message': 'Question deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def publish_form(request, form_uuid):
    """Publish/unpublish form"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    form_obj.is_published = not form_obj.is_published
    form_obj.save()
    
    status = 'published' if form_obj.is_published else 'unpublished'
    messages.success(request, f'Form {status} successfully!')
    return redirect('edit_form', form_uuid=form_uuid)

# CRITICAL: This view MUST NOT have @login_required decorator
def form_public_view(request, form_uuid):
    """Public form view for respondents - WORKS FOR ANYONE (logged in or anonymous)"""
    try:
        form_obj = get_object_or_404(Form, uuid=form_uuid, is_published=True)
    except:
        return render(request, 'forms/form_not_found.html')
    
    # Check if form is within schedule
    if not form_obj.is_open:
        return render(request, 'forms/form_closed.html', {'form': form_obj})
    
    questions = form_obj.questions.all().order_by('order')
    
    if request.method == 'POST':
        try:
            # Create response (works for both anonymous and logged-in users)
            response = Response.objects.create(
                form=form_obj,
                respondent_email=request.POST.get('respondent_email', '') if form_obj.collect_email else None,
                respondent_name=request.POST.get('respondent_name', ''),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )

            # Process each question's answer
            for question in questions:
                field_name = f'question_{question.id}'
                
                if question.question_type in ['multiple_choice', 'dropdown']:
                    if field_name in request.POST and request.POST[field_name]:
                        try:
                            option = Option.objects.get(id=request.POST[field_name])
                            answer = Answer.objects.create(response=response, question=question)
                            answer.selected_options.add(option)
                        except Option.DoesNotExist:
                            pass
                
                elif question.question_type == 'checkboxes':
                    option_ids = request.POST.getlist(field_name)
                    if option_ids:
                        answer = Answer.objects.create(response=response, question=question)
                        for option_id in option_ids:
                            try:
                                option = Option.objects.get(id=option_id)
                                answer.selected_options.add(option)
                            except Option.DoesNotExist:
                                pass
                
                elif question.question_type == 'file_upload':
                    if field_name in request.FILES:
                        Answer.objects.create(
                            response=response,
                            question=question,
                            file_upload=request.FILES[field_name]
                        )
                
                else:  # Text-based answers (short_text, long_text, date, time, linear_scale)
                    if field_name in request.POST and request.POST[field_name].strip():
                        Answer.objects.create(
                            response=response,
                            question=question,
                            answer_text=request.POST[field_name].strip()
                        )

            # NEW: Handle Change model - get date from form or use current date
            change_date_value = request.POST.get('change_date', '')
            if change_date_value:
                # User provided a date, parse it
                from datetime import datetime
                try:
                    parsed_date = datetime.strptime(change_date_value, '%Y-%m-%d').date()
                    Change.objects.create(change_date=parsed_date)
                    print(f"Change record created with user-selected date: {parsed_date}")  # Debug
                except ValueError:
                    # Invalid date format, use current date
                    Change.objects.create(change_date=date.today())
                    print(f"Invalid date format, created change with current date: {date.today()}")  # Debug
            else:
                # No date provided, use current date
                Change.objects.create(change_date=date.today())
                print(f"No date provided, created change with current date: {date.today()}")  # Debug

            # Send email notification to form owner
            if form_obj.send_email_notifications and form_obj.user.email:
                try:
                    send_mail(
                        subject=f'New Response: {form_obj.title}',
                        message=f'You have received a new response for your form "{form_obj.title}".\n\nView responses: {request.build_absolute_uri(reverse("view_responses", kwargs={"form_uuid": form_obj.uuid}))}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[form_obj.user.email],
                        fail_silently=True,
                    )
                except:
                    pass  # Fail silently if email sending fails

            return render(request, 'forms/form_submitted.html', {'form': form_obj})
            
        except Exception as e:
            print(f"Error processing form submission: {e}")
            return render(request, 'forms/form_public.html', {
                'form': form_obj,
                'questions': questions,
                'error': 'There was an error submitting your response. Please try again.'
            })
    
    # GET request - show the form
    context = {
        'form': form_obj,
        'questions': questions,
    }
    return render(request, 'forms/form_public.html', context)

@login_required
def view_responses(request, form_uuid):
    """View form responses - ONLY for form owner"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    responses = form_obj.responses.all().order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(responses, 20)
    page_number = request.GET.get('page')
    responses_page = paginator.get_page(page_number)
    
    questions = form_obj.questions.all().order_by('order')
    
    context = {
        'form': form_obj,
        'responses': responses_page,
        'questions': questions,
        'total_responses': responses.count(),
    }
    return render(request, 'forms/view_responses.html', context)

@login_required
def form_analytics(request, form_uuid):
    """Form analytics and statistics - ONLY for form owner"""
    form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
    questions = form_obj.questions.all().order_by('order')
    
    analytics_data = {}
    
    for question in questions:
        if question.question_type in ['multiple_choice', 'dropdown', 'checkboxes']:
            # Get option counts
            option_counts = {}
            for option in question.options.all():
                count = Answer.objects.filter(
                    question=question,
                    selected_options=option
                ).count()
                option_counts[option.text] = count
            
            analytics_data[question.id] = {
                'type': 'chart',
                'question': question.text,
                'data': option_counts
            }
        
        elif question.question_type == 'linear_scale':
            # Get scale counts
            scale_counts = {}
            scale_min = question.scale_min or 1
            scale_max = question.scale_max or 5
            
            for i in range(scale_min, scale_max + 1):
                count = Answer.objects.filter(
                    question=question,
                    answer_text=str(i)
                ).count()
                scale_counts[str(i)] = count
            
            analytics_data[question.id] = {
                'type': 'chart',
                'question': question.text,
                'data': scale_counts
            }
        
        else:
            # Text responses
            answers = Answer.objects.filter(question=question).exclude(answer_text__isnull=True).exclude(answer_text='').values_list('answer_text', flat=True)
            analytics_data[question.id] = {
                'type': 'text',
                'question': question.text,
                'answers': list(answers)[:10]  # Show first 10 responses
            }
    
    context = {
        'form': form_obj,
        'analytics_data': analytics_data,
        'total_responses': form_obj.response_count,
    }
    return render(request, 'forms/analytics.html', context)

@login_required
def delete_form(request, form_uuid):
    """Delete a form"""
    if request.method == 'POST':
        form_obj = get_object_or_404(Form, uuid=form_uuid, user=request.user)
        form_title = form_obj.title
        form_obj.delete()
        messages.success(request, f'Form "{form_title}" deleted successfully!')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
@require_http_methods(['POST'])
def toggle_dark_mode(request):
    """Toggle dark mode preference"""
    try:
        if UserProfile:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.dark_mode = not profile.dark_mode
            profile.save()
            return JsonResponse({
                'success': True,
                'dark_mode': profile.dark_mode,
                'message': f'Dark mode {"enabled" if profile.dark_mode else "disabled"}'
            })
    except:
        pass
    return JsonResponse({
        'success': False,
        'message': 'Error toggling dark mode'
    }, status=400)

def get_user_theme(request):
    """Get user's theme preference"""
    if request.user.is_authenticated and UserProfile:
        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            return {'dark_mode': profile.dark_mode}
        except:
            pass
    return {'dark_mode': False}

# Context processor for theme
def theme_context(request):
    return get_user_theme(request)
