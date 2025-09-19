from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Form management
    path('create/', views.create_form, name='create_form'),
    path('edit/<uuid:form_uuid>/', views.edit_form, name='edit_form'),
    path('delete/<uuid:form_uuid>/', views.delete_form, name='delete_form'),
    path('publish/<uuid:form_uuid>/', views.publish_form, name='publish_form'),
    
    # Form settings
    path('update-settings/<uuid:form_uuid>/', views.update_form_settings, name='update_form_settings'),
    
    # Question management
    path('add-question/<uuid:form_uuid>/', views.add_question, name='add_question'),
    path('update-question/<int:question_id>/', views.update_question, name='update_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    
    # CRITICAL: Public form access (MUST be accessible to anonymous users)
    path('form/<uuid:form_uuid>/', views.form_public_view, name='form_public_view'),
    
    # Response management (ONLY for form owner)
    path('responses/<uuid:form_uuid>/', views.view_responses, name='view_responses'),
    path('analytics/<uuid:form_uuid>/', views.form_analytics, name='form_analytics'),
    
    # Theme toggle
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
]
