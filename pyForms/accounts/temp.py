from django.contrib.auth.models import User
from forms.models import Form, Question, Option, Response, Answer
from django.utils import timezone
from faker import Faker
import random

fake = Faker()

# Create or get a realistic demo user
demo_user, created = User.objects.get_or_create(
    username='janedoe',
    defaults={
        'email': 'janedoe@example.com',
        'first_name': 'Jane',
        'last_name': 'Doe'
    }
)
if created:
    demo_user.set_password('SecurePass123')
    demo_user.save()

theme_choices = ['blue', 'red', 'green', 'purple', 'orange', 'teal', 'pink', 'indigo', 'custom']
question_types = [
    'short_text', 'long_text', 'multiple_choice', 'checkboxes', 'dropdown',
    'linear_scale', 'multiple_choice_grid', 'date', 'time', 'file_upload'
]

forms = []
for _ in range(20):
    form_title = fake.catch_phrase()
    form_description = fake.paragraph(nb_sentences=2)
    form = Form.objects.create(
        user=demo_user,
        title=form_title,
        description=form_description,
        is_published=random.choice([True, False]),
        allow_multiple_responses=random.choice([True, False]),
        collect_email=random.choice([True, False]),
        open_date=timezone.now() - timezone.timedelta(days=random.randint(0, 10)),
        close_date=timezone.now() + timezone.timedelta(days=random.randint(10, 60)),
        theme_color=random.choice(theme_choices),
        custom_color="#%06x" % random.randint(0, 0xFFFFFF) if random.choice([True, False]) else None,
        send_email_notifications=random.choice([True, False])
    )
    forms.append(form)

print(f"Created {len(forms)} forms")

all_questions = []
for form in forms:
    num_questions = random.randint(5, 10)
    for order in range(num_questions):
        q_type = random.choice(question_types)

        # Craft realistic question texts based on type
        if q_type == 'short_text':
            q_text = f"What is your current {fake.job()}?"
        elif q_type == 'long_text':
            q_text = f"Please describe your experience with {fake.bs()}."
        elif q_type == 'multiple_choice':
            q_text = "Which of the following best describes your industry?"
        elif q_type == 'checkboxes':
            q_text = "Select all services you have used recently."
        elif q_type == 'dropdown':
            q_text = "Choose your preferred working location."
        elif q_type == 'linear_scale':
            q_text = "Rate your satisfaction from low to high."
        elif q_type == 'multiple_choice_grid':
            q_text = "Please rate the following aspects of our service."
        elif q_type == 'date':
            q_text = "When did you start your current job?"
        elif q_type == 'time':
            q_text = "At what time do you normally start work?"
        elif q_type == 'file_upload':
            q_text = "Upload a relevant document for verification."
        else:
            q_text = "General question."

        question = Question.objects.create(
            form=form,
            text=q_text,
            help_text=fake.sentence(),
            question_type=q_type,
            is_required=random.choice([True, False]),
            order=order,
            scale_min=1 if q_type == 'linear_scale' else None,
            scale_max=5 if q_type == 'linear_scale' else None,
            scale_min_label='Low' if q_type == 'linear_scale' else None,
            scale_max_label='High' if q_type == 'linear_scale' else None,
        )
        all_questions.append(question)

        # Create options for specific question types
        if q_type in ['multiple_choice', 'checkboxes', 'dropdown', 'multiple_choice_grid']:
            num_options = random.randint(3, 6)
            for idx in range(num_options):
                option_text = fake.word().capitalize()
                Option.objects.create(
                    question=question,
                    text=option_text,
                    order=idx
                )

print(f"Created {len(all_questions)} questions with options where applicable.")

# Create sample responses and answers
for form in forms:
    for _ in range(random.randint(1, 3)):  # 1-3 responses per form
        response = Response.objects.create(
            form=form,
            ip_address=fake.ipv4_private(),
            user_agent=fake.user_agent(),
            respondent_email=fake.email(),
            respondent_name=fake.name()
        )

        for question in form.questions.all():
            answer_text = None
            selected_options = []

            if question.question_type in ['multiple_choice', 'checkboxes', 'dropdown', 'multiple_choice_grid']:
                options = list(question.options.all())
                selected_count = 1 if question.question_type == 'multiple_choice' else random.randint(1, min(3, len(options)))
                selected_options = random.sample(options, selected_count)
            elif question.question_type == 'short_text':
                answer_text = fake.word()
            elif question.question_type == 'long_text':
                answer_text = fake.paragraph()
            elif question.question_type == 'date':
                answer_text = str(fake.date_between(start_date='-5y', end_date='today'))
            elif question.question_type == 'time':
                answer_text = str(fake.time())
            elif question.question_type == 'linear_scale':
                answer_text = str(random.randint(1, 5))
            elif question.question_type == 'file_upload':
                answer_text = None  # File uploads won't be handled here

            answer = Answer.objects.create(
                response=response,
                question=question,
                answer_text=answer_text
            )
            if selected_options:
                answer.selected_options.set(selected_options)

print("Created demo responses and answers with realistic data.")