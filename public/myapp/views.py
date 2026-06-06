
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from django.db.models import Count


# ------------------------------------------------
# Basic Pages
# ------------------------------------------------
def index(request):
    return render(request, 'index.html')


# ------------------------------------------------
# 1. Login & Logout
# ------------------------------------------------
def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username")
        p = request.POST.get("password")

        user = authenticate(username=u, password=p)

        if user is not None:
            # actually log the user in (important!)
            auth_login(request, user)

            # If it's a Django admin / superuser / userType == 'admin'
            if user.is_superuser or user.is_staff or user.userType == "admin":
                request.session['lid'] = user.id
                request.session['admin_id'] = user.id
                messages.success(request, "Login successful (admin)")
                return redirect("admin_dashboard")

            elif user.userType == "organizer":
                # Check if blocked/rejected
                org_obj = Organizer.objects.filter(loginid=user).first()
                if org_obj and org_obj.status == "rejected":
                    messages.error(request, "Your account has been blocked by admin.")
                    return redirect("/login/")
                elif org_obj and org_obj.status == "pending":
                    messages.error(request, "Your account is pending admin approval.")
                    return redirect("/login/")

                request.session['organizer_id'] = user.id
                request.session['lid'] = user.id
                messages.success(request, "Login successful (organizer)")
                return redirect("organizer_dashboard")

            elif user.userType == "volunteer":
                request.session['volunteer_id'] = user.id
                request.session['lid'] = user.id
                messages.success(request, "Login successful (volunteer)")
                return redirect("volunteer_dashboard")

            # If user has no matching usertype
            messages.error(request, "User type not allowed or not set.")
            return render(request, "login.html")

        else:
            messages.error(request, "Invalid username or password")
            return render(request, "login.html")

    return render(request, "login.html")

def logout_view(request):
    auth_logout(request)
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('index')


# ------------------------------------------------
# 2. Registration
# ------------------------------------------------
def register_volunteer(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        ph = request.POST.get('phone')
        e = request.POST.get('email')
        addr = request.POST.get('address')
        
        if Login.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_volunteer')
            
        user = Login.objects.create_user(username=u, password=p, userType='volunteer', viewPass=p)
        Volunteer.objects.create(loginid=user, name=n, phone=ph, email=e, address=addr)
        
        messages.success(request, 'Registration successful. You can now login.')
        return redirect('login')
        
    return render(request, 'register_volunteer.html')

def register_organizer(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        org_name = request.POST.get('organization_name')
        cp = request.POST.get('contact_person')
        ph = request.POST.get('phone')
        e = request.POST.get('email')
        addr = request.POST.get('address')
        
        if Login.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_organizer')
            
        user = Login.objects.create_user(username=u, password=p, userType='organizer', viewPass=p)
        Organizer.objects.create(loginid=user, organization_name=org_name, contact_person=cp, phone=ph, email=e, address=addr)
        
        messages.success(request, 'Registration submitted. Please wait for admin approval.')
        return redirect('login')
        
    return render(request, 'register_organizer.html')


# ------------------------------------------------
# 3. Admin Home & Views
# ------------------------------------------------
@login_required
def admin_dashboard(request):
    total_organizers = Organizer.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_events = Event.objects.count()
    
    context = {
        'total_organizers': total_organizers,
        'total_volunteers': total_volunteers,
        'total_events': total_events
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def manage_organizers(request):
    organizers = Organizer.objects.all()
    return render(request, 'admin/manage_organizers.html', {'organizers': organizers})

@login_required
def approve_organizer(request, org_id):
    org = Organizer.objects.get(id=org_id)
    org.status = 'approved'
    org.save()
    messages.success(request, f'Organizer {org.organization_name} approved.')
    return redirect('manage_organizers')

@login_required
def reject_organizer(request, org_id):
    org = Organizer.objects.get(id=org_id)
    org.status = 'rejected'
    org.save()
    messages.success(request, f'Organizer {org.organization_name} rejected.')
    return redirect('manage_organizers')


# ------------------------------------------------
# 4. Organizer Home & Views
# ------------------------------------------------
@login_required
def organizer_dashboard(request):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    if org.status != 'approved':
        return render(request, 'organizer/pending_approval.html')
        
    events = Event.objects.filter(organizer=org)
    return render(request, 'organizer/dashboard.html', {'events': events, 'org': org})

@login_required
def create_event(request):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        cat_id = request.POST.get('category')
        date = request.POST.get('date')
        time = request.POST.get('time')
        loc = request.POST.get('location')
        max_v = request.POST.get('max_volunteers')
        
        cat = Category.objects.get(id=cat_id) if cat_id else None
        
        Event.objects.create(
            organizer=org, title=title, description=desc, category=cat,
            date=date, time=time, location=loc, max_volunteers=max_v
        )
        messages.success(request, 'Event created successfully')
        return redirect('organizer_dashboard')
        
    categories = Category.objects.all()
    return render(request, 'organizer/create_event.html', {'categories': categories})

@login_required
def organizer_event_details(request, event_id):
    event = Event.objects.get(id=event_id)
    applications = Application.objects.filter(event=event)
    tasks = Task.objects.filter(event=event)
    
    return render(request, 'organizer/event_details.html', {
        'event': event, 
        'applications': applications, 
        'tasks': tasks
    })


@login_required
def organizer_profile(request):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    if request.method == 'POST':
        org.organization_name = request.POST.get('organization_name', org.organization_name)
        org.contact_person    = request.POST.get('contact_person',    org.contact_person)
        org.phone             = request.POST.get('phone',             org.phone)
        org.email             = request.POST.get('email',             org.email)
        org.address           = request.POST.get('address',           org.address)
        org.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('organizer_profile')

    return render(request, 'organizer/profile.html', {'org': org})


# ------------------------------------------------
# 5. Volunteer Home & Views
# ------------------------------------------------
@login_required
def volunteer_dashboard(request):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    upcoming_events = Event.objects.filter(status='Upcoming')
    
    return render(request, 'volunteer/dashboard.html', {
        'events': upcoming_events, 
        'vol': vol
    })

@login_required
def apply_event(request, event_id):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    event = Event.objects.get(id=event_id)
    
    if not Application.objects.filter(volunteer=vol, event=event).exists():
        Application.objects.create(volunteer=vol, event=event)
        messages.success(request, f'Successfully applied for {event.title}')
    else:
        messages.info(request, 'You have already applied for this event.')
        
    return redirect('volunteer_dashboard')

@login_required
def volunteer_profile(request):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    if request.method == 'POST':
        vol.name = request.POST.get('name')
        vol.phone = request.POST.get('phone')
        vol.email = request.POST.get('email')
        vol.address = request.POST.get('address')
        
        # Skills & Interests ManyToMany
        skill_ids = request.POST.getlist('skills')
        interest_ids = request.POST.getlist('interests')
        
        if skill_ids:
            vol.skills.set(skill_ids)
        else:
            vol.skills.clear()
            
        if interest_ids:
            vol.interests.set(interest_ids)
        else:
            vol.interests.clear()
            
        # Profile Picture file upload
        if 'profile_pic' in request.FILES:
            vol.profile_pic = request.FILES['profile_pic']
            
        vol.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('volunteer_profile')
        
    skills = Skill.objects.all()
    categories = Category.objects.all()
    
    return render(request, 'volunteer/profile.html', {
        'vol': vol,
        'skills': skills,
        'categories': categories
    })


# =========================================================
# Administrator Views
# =========================================================
@login_required
def admin_manage_volunteers(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    volunteers = Volunteer.objects.all()
    return render(request, 'admin/manage_volunteers.html', {'volunteers': volunteers})

@login_required
def admin_toggle_volunteer(request, vol_id):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    vol = Volunteer.objects.get(id=vol_id)
    login_obj = vol.loginid
    login_obj.is_active = not login_obj.is_active
    login_obj.save()
    status_str = "activated" if login_obj.is_active else "blocked"
    messages.success(request, f"Volunteer {vol.name} has been {status_str}.")
    return redirect('admin_manage_volunteers')

@login_required
def admin_monitor_events(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    events = Event.objects.all().order_by('-created_at')
    return render(request, 'admin/monitor_events.html', {'events': events})

@login_required
def admin_manage_categories(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        if name:
            Category.objects.create(name=name, description=desc)
            messages.success(request, f"Category '{name}' created successfully.")
        return redirect('admin_manage_categories')
    categories = Category.objects.all()
    return render(request, 'admin/manage_categories.html', {'categories': categories})

@login_required
def admin_delete_category(request, cat_id):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    cat = Category.objects.get(id=cat_id)
    cat.delete()
    messages.success(request, "Category deleted successfully.")
    return redirect('admin_manage_categories')

@login_required
def admin_manage_skills(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    if request.method == 'POST':
        name = request.POST.get('name')
        desc = request.POST.get('description')
        if name:
            Skill.objects.create(name=name, description=desc)
            messages.success(request, f"Skill '{name}' created successfully.")
        return redirect('admin_manage_skills')
    skills = Skill.objects.all()
    return render(request, 'admin/manage_skills.html', {'skills': skills})

@login_required
def admin_delete_skill(request, skill_id):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    skill = Skill.objects.get(id=skill_id)
    skill.delete()
    messages.success(request, "Skill deleted successfully.")
    return redirect('admin_manage_skills')

@login_required
def admin_feedback(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        reply = request.POST.get('reply')
        fb = Feedback.objects.get(id=feedback_id)
        fb.reply = reply
        fb.status = 'Resolved'
        fb.save()
        messages.success(request, "Reply sent successfully.")
        return redirect('admin_feedback')
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'admin/feedback.html', {'feedbacks': feedbacks})

@login_required
def admin_report(request):
    if not (request.user.is_superuser or request.user.userType == 'admin'):
        return redirect('login')
    
    total_events = Event.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_organizers = Organizer.objects.count()
    
    # Participation Stats
    total_applications = Application.objects.count()
    approved_applications = Application.objects.filter(status='Approved').count()
    
    # Average performance rating
    from django.db.models import Avg
    avg_rating = PerformanceReview.objects.aggregate(Avg('rating'))['rating__avg']
    if avg_rating is None:
        avg_rating = 0.0
    
    # Event statuses
    event_statuses = Event.objects.values('status').annotate(count=Count('status'))
    
    context = {
        'total_events': total_events,
        'total_volunteers': total_volunteers,
        'total_organizers': total_organizers,
        'total_applications': total_applications,
        'approved_applications': approved_applications,
        'avg_rating': round(avg_rating, 2),
        'event_statuses': event_statuses,
        'events': Event.objects.all().order_by('-date'),
        'volunteers': Volunteer.objects.all()
    }
    return render(request, 'admin/report.html', context)


# =========================================================
# Event Organizer Views
# =========================================================
@login_required
def update_application_status(request, app_id, status):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    app = Application.objects.get(id=app_id, event__organizer=org)
    
    if status in ['Approved', 'Rejected']:
        app.status = status
        app.save()
        messages.success(request, f"Application for {app.volunteer.name} set to {status}.")
        
        # Create notification for volunteer
        Notification.objects.create(
            user=app.volunteer.loginid,
            message=f"Your application for event '{app.event.title}' has been {status.lower()}."
        )
    return redirect('organizer_event_details', event_id=app.event.id)

@login_required
def create_task(request, event_id):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    event = Event.objects.get(id=event_id, organizer=org)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('description')
        skill_ids = request.POST.getlist('required_skills')
        
        task = Task.objects.create(event=event, title=title, description=desc)
        if skill_ids:
            task.required_skills.set(skill_ids)
            
        messages.success(request, f"Task '{title}' created successfully.")
        return redirect('organizer_event_details', event_id=event.id)
        
    skills = Skill.objects.all()
    return render(request, 'organizer/create_task.html', {'event': event, 'skills': skills})

@login_required
def assign_task(request, task_id):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    task = Task.objects.get(id=task_id, event__organizer=org)
    
    if request.method == 'POST':
        vol_id = request.POST.get('volunteer')
        vol = Volunteer.objects.get(id=vol_id)
        
        # Check if already assigned
        if TaskAssignment.objects.filter(task=task, volunteer=vol).exists():
            messages.info(request, f"Task is already assigned to {vol.name}.")
        else:
            TaskAssignment.objects.create(task=task, volunteer=vol)
            messages.success(request, f"Task assigned to {vol.name} successfully.")
            # Notify volunteer
            Notification.objects.create(
                user=vol.loginid,
                message=f"You have been assigned a new task: '{task.title}' under event '{task.event.title}'."
            )
        return redirect('organizer_event_details', event_id=task.event.id)
        
    # Get approved volunteers for this event
    approved_apps = Application.objects.filter(event=task.event, status='Approved')
    volunteers = [app.volunteer for app in approved_apps]
    return render(request, 'organizer/assign_task.html', {'task': task, 'volunteers': volunteers})

@login_required
def track_attendance(request, event_id):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    event = Event.objects.get(id=event_id, organizer=org)
    approved_apps = Application.objects.filter(event=event, status='Approved')
    
    if request.method == 'POST':
        present_vol_ids = request.POST.getlist('attendance')
        
        for app in approved_apps:
            vol = app.volunteer
            is_present = str(vol.id) in present_vol_ids
            Attendance.objects.update_or_create(
                event=event, volunteer=vol,
                defaults={'is_present': is_present}
            )
        
        event.status = 'Completed'
        event.save()
        
        messages.success(request, "Attendance tracked successfully. Event marked as Completed.")
        return redirect('organizer_event_details', event_id=event.id)
        
    attendance_records = {att.volunteer_id: att.is_present for att in Attendance.objects.filter(event=event)}
    return render(request, 'organizer/track_attendance.html', {
        'event': event, 
        'approved_apps': approved_apps,
        'attendance_records': attendance_records
    })

@login_required
def evaluate_performance(request, event_id):
    org = Organizer.objects.get(loginid_id=request.session['lid'])
    event = Event.objects.get(id=event_id, organizer=org)
    
    present_att = Attendance.objects.filter(event=event, is_present=True)
    volunteers = [att.volunteer for att in present_att]
    
    if request.method == 'POST':
        for vol in volunteers:
            rating = request.POST.get(f'rating_{vol.id}', 0)
            remarks = request.POST.get(f'remarks_{vol.id}', '')
            
            PerformanceReview.objects.update_or_create(
                event=event, volunteer=vol,
                defaults={'rating': int(rating), 'remarks': remarks}
            )
            
            Notification.objects.create(
                user=vol.loginid,
                message=f"You received a performance evaluation for the event '{event.title}'."
            )
            
        messages.success(request, "Evaluations submitted successfully.")
        return redirect('organizer_event_details', event_id=event.id)
        
    reviews = {rev.volunteer_id: rev for rev in PerformanceReview.objects.filter(event=event)}
    return render(request, 'organizer/evaluate_performance.html', {
        'event': event,
        'volunteers': volunteers,
        'reviews': reviews
    })


# =========================================================
# Volunteer Views
# =========================================================
@login_required
def volunteer_tasks(request):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    assignments = TaskAssignment.objects.filter(volunteer=vol).order_by('-assigned_at')
    return render(request, 'volunteer/tasks.html', {'assignments': assignments})

@login_required
def update_task_assignment_status(request, assignment_id):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    assignment = TaskAssignment.objects.get(id=assignment_id, volunteer=vol)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Assigned', 'In Progress', 'Completed']:
            assignment.status = new_status
            assignment.save()
            
            task = assignment.task
            task.status = new_status
            task.save()
            
            messages.success(request, f"Task status updated to {new_status}.")
    return redirect('volunteer_tasks')

@login_required
def volunteer_history(request):
    vol = Volunteer.objects.get(loginid_id=request.session['lid'])
    applications = Application.objects.filter(volunteer=vol).order_by('-applied_at')
    
    reviews = PerformanceReview.objects.filter(volunteer=vol)
    reviews_dict = {rev.event_id: rev for rev in reviews}
    
    attendance = Attendance.objects.filter(volunteer=vol)
    attendance_dict = {att.event_id: att.is_present for att in attendance}
    
    history_data = []
    for app in applications:
        event = app.event
        history_data.append({
            'event': event,
            'app_status': app.status,
            'is_present': attendance_dict.get(event.id, None),
            'review': reviews_dict.get(event.id, None)
        })
        
    return render(request, 'volunteer/history.html', {'history': history_data})

@login_required
def view_certificate(request, review_id):
    review = PerformanceReview.objects.get(id=review_id)
    
    is_authorized = False
    if request.user.is_superuser or request.user.userType == 'admin':
        is_authorized = True
    elif request.user.userType == 'volunteer' and review.volunteer.loginid == request.user:
        is_authorized = True
    elif request.user.userType == 'organizer' and review.event.organizer.loginid == request.user:
        is_authorized = True
        
    if not is_authorized:
        return redirect('index')
        
    return render(request, 'organizer/certificate.html', {'review': review})


# =========================================================
# Feedback / Complaints Views
# =========================================================
@login_required
def submit_feedback(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        if subject and message:
            Feedback.objects.create(user=request.user, subject=subject, message=message)
            messages.success(request, "Feedback submitted successfully.")
            return redirect('submit_feedback')
            
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'submit_feedback.html', {'feedbacks': feedbacks})

