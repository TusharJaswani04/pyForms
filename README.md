# pyForms - Django Form Builder

A comprehensive Django-based form builder application similar to Google Forms, allowing users to create, manage, and analyze custom forms with advanced features.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [API Endpoints](#api-endpoints)

## 🎯 Overview

pyForms is a powerful, user-friendly form builder that enables users to create dynamic forms, collect responses, and analyze data through intuitive dashboards and analytics. Built with Django and modern web technologies, it provides a seamless experience for both form creators and respondents.

**Key Highlights:**
- Google Forms-like interface and functionality
- Real-time form building with drag-and-drop features
- Comprehensive analytics and data visualization
- Responsive design for all devices
- User authentication and form ownership
- Email notifications and data export capabilities

## ✨ Features

### 🔧 Form Creation & Management
- **Intuitive Form Builder**: Create forms with various question types
- **Multiple Question Types**: 
  - Short text and long text
  - Multiple choice and checkboxes
  - Dropdown menus
  - Linear scales (rating)
  - Date and time pickers
  - File upload support
- **Form Customization**: Themes, colors, header images
- **Form Scheduling**: Set open/close dates for forms
- **Draft & Publish**: Save drafts and publish when ready

### 👥 User & Response Management
- **User Authentication**: Secure login/signup system
- **Response Collection**: Anonymous or authenticated responses
- **Email Integration**: Collect respondent emails (optional)
- **Response Tracking**: IP address and user agent logging
- **Change Tracking**: Date-based change records for submissions

### 📊 Analytics & Insights
- **Dashboard Overview**: Form statistics and response counts
- **Visual Analytics**: Charts and graphs for response data
- **Response Viewing**: Detailed response tables with pagination
- **Data Export**: Export responses to various formats
- **Real-time Updates**: Live response tracking

### 🎨 User Experience
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Modern UI**: Clean, Google Forms-inspired interface
- **Real-time Validation**: Instant form validation feedback
- **Progress Indicators**: Visual progress during form submission
- **Error Handling**: Comprehensive error messages and recovery

## 🛠 Tech Stack

### Backend
- **Framework**: Django 5.2.5
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication system
- **Forms**: Django Forms + Crispy Forms for styling
- **Email**: Django's email framework with SMTP support

### Frontend
- **Styling**: Bootstrap 5 + Custom CSS
- **Icons**: Bootstrap Icons
- **Fonts**: Google Fonts (Google Sans)
- **JavaScript**: Vanilla JS for interactions
- **Charts**: Chart.js for analytics visualization

### Additional Technologies
- **File Storage**: Django's file handling system
- **Template Engine**: Django Templates
- **Form Styling**: Django Crispy Forms with Bootstrap5
- **Image Processing**: Pillow for image handling

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/pyforms.git
   cd pyforms
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Create .env file in project root
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

9. **Access the Application**
   - Open browser and go to: `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin`

## 🎮 Usage

### Creating Your First Form

1. **Sign Up/Login**: Create an account or login to existing account
2. **Dashboard**: Navigate to your dashboard to see form overview
3. **Create Form**: Click "Create Form" button
4. **Form Settings**: 
   - Enter form title and description
   - Configure email collection and notification settings
   - Choose theme colors
5. **Add Questions**: 
   - Click "Add Question" to add new questions
   - Choose question types (text, multiple choice, etc.)
   - Configure question settings (required, help text, etc.)
6. **Publish Form**: Toggle publish status to make form public
7. **Share Form**: Copy the public form link to share with respondents

### Collecting Responses

1. **Public Access**: Share form URL with respondents
2. **Response Submission**: Respondents fill out form (with optional change date)
3. **Automatic Processing**: Responses saved automatically to database
4. **Email Notifications**: Optional email notifications sent to form owner

### Viewing Analytics

1. **Response Dashboard**: View all responses in tabular format
2. **Analytics Page**: Access charts and visual analytics
3. **Export Data**: Download response data in various formats
4. **Change Tracking**: Monitor submission dates and changes

## 📁 Project Structure

```
pyforms/
│
├── pyforms/                    # Main project directory
│   ├── settings.py            # Django settings
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py               # WSGI configuration
│
├── forms/                     # Forms app (main application)
│   ├── models.py             # Database models (Form, Question, Response, etc.)
│   ├── views.py              # View functions and form handling
│   ├── urls.py               # Forms app URL patterns
│   ├── admin.py              # Django admin configuration
│   ├── forms.py              # Django form classes
│   └── migrations/           # Database migrations
│
├── accounts/                  # User authentication app
│   ├── models.py             # User profile models
│   ├── views.py              # Authentication views
│   └── urls.py               # Auth URL patterns
│
├── templates/                 # HTML templates
│   ├── base/                 # Base templates
│   ├── forms/                # Form-related templates
│   │   ├── dashboard.html    # User dashboard
│   │   ├── create_form.html  # Form creation page
│   │   ├── edit_form.html    # Form editing interface
│   │   ├── form_public.html  # Public form view
│   │   ├── view_responses.html # Response viewing
│   │   └── analytics.html    # Analytics dashboard
│   └── accounts/             # Authentication templates
│
├── static/                   # Static files (CSS, JS, images)
│   ├── css/                  # Custom stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Static images
│
├── media/                    # User uploaded files
│   ├── form_headers/         # Form header images
│   └── form_files/           # Response file uploads
│
├── requirements.txt          # Python dependencies
├── manage.py                # Django management script
└── README.md                # Project documentation
```

## 📸 Screenshots

### Dashboard Overview
![Dashboard](screenshots/dashboard.png)
*User dashboard showing form statistics and management options*

### Form Builder
![Form Builder](screenshots/form-builder.png)
*Interactive form building interface with question management*

### Public Form
![Public Form](screenshots/public-form.png)
*Clean, responsive public form interface for respondents*

### Analytics Dashboard
![Analytics](screenshots/analytics.png)
*Comprehensive analytics with charts and response visualization*

## 🔌 API Endpoints

### Form Management
```
POST /forms/create/                    # Create new form
GET  /forms/edit/<uuid>/              # Edit form interface
POST /forms/<uuid>/settings/          # Update form settings (AJAX)
POST /forms/<uuid>/questions/add/     # Add question (AJAX)
PUT  /forms/questions/<id>/update/    # Update question (AJAX)
DELETE /forms/questions/<id>/delete/  # Delete question (AJAX)
```

### Response Handling
```
GET  /form/<uuid>/                    # Public form view
POST /form/<uuid>/                    # Submit form response
GET  /forms/<uuid>/responses/         # View responses (owner only)
GET  /forms/<uuid>/analytics/         # View analytics (owner only)
```

### User Management
```
GET  /dashboard/                      # User dashboard
POST /accounts/login/                 # User login
POST /accounts/register/              # User registration
POST /accounts/logout/                # User logout
```

## 🤝 Contributing

We welcome contributions to pyForms! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python manage.py test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 Python style guidelines
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure responsive design compatibility

### Areas for Contribution
- 🐛 Bug fixes and improvements
- ✨ New question types or form features
- 📊 Enhanced analytics and reporting
- 🎨 UI/UX improvements
- 🔒 Security enhancements
- 📱 Mobile experience optimization
- 🌐 Internationalization (i18n)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Framework**: For providing a robust web framework
- **Bootstrap**: For responsive UI components
- **Google Forms**: For UI/UX inspiration
- **Chart.js**: For beautiful data visualizations
- **Bootstrap Icons**: For comprehensive icon library

*Star ⭐ this repository if you found it helpful!*
