# Impact_Crew

Impact_Crew is a comprehensive Django-based Volunteer Management System designed to connect organizers with volunteers efficiently. The platform features three distinct user roles: **Admin**, **Organizer**, and **Volunteer**.

## Key Features

### 👤 Volunteer
- **Profile Management**: Register and manage your profile with specific skills and interests.
- **Event Participation**: Browse and apply for upcoming events and activities.
- **Task Management**: Accept and update the status of assigned tasks.
- **Performance & History**: View past event history, performance reviews, and view certificates.

### 🏢 Organizer
- **Event Creation**: Plan and publish new events and activities.
- **Volunteer Management**: Review and approve/reject volunteer applications.
- **Task Assignment**: Create tasks within events and assign them to approved volunteers.
- **Tracking & Evaluation**: Track volunteer attendance and evaluate their performance post-event.

### 👑 Admin
- **Dashboard & Monitoring**: Comprehensive dashboard to monitor all platform activities and events.
- **User Management**: Approve/reject organizer accounts and manage volunteer statuses.
- **System Configuration**: Manage event categories and required skills.
- **Support**: Handle user feedback, complaints, and generate reports.

## Setup Instructions

1. **Activate the virtual environment**:
   - Windows: `env\Scripts\activate`
   - Unix/MacOS: `source env/bin/activate`
2. **Navigate to the application directory**:
   - `cd public`
3. **Run Database Migrations**:
   - `python manage.py makemigrations`
   - `python manage.py migrate`
4. **Start the Development Server**:
   - `python manage.py runserver`
5. **Access the application**:
   - Open your web browser and go to `http://127.0.0.1:8000/`
