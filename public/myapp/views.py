from django.shortcuts import render, redirect, get_object_or_404
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
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        
        if user is not None:
            auth_login(request, user)
            
            if user.userType == 'admin':
                messages.success(request, 'Login successful (Admin)')
                return redirect('admin_dashboard')
                
            elif user.userType == 'organizer':
                messages.success(request, 'Login successful (Organizer)')
                return redirect('organizer_dashboard')
                
            elif user.userType == 'volunteer':
                messages.success(request, 'Login successful (Volunteer)')
                return redirect('volunteer_dashboard')
                
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
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
    org = get_object_or_404(Organizer, id=org_id)
    org.status = 'approved'
    org.save()
    messages.success(request, f'Organizer {org.organization_name} approved.')
    return redirect('manage_organizers')

@login_required
def reject_organizer(request, org_id):
    org = get_object_or_404(Organizer, id=org_id)
    org.status = 'rejected'
    org.save()
    messages.success(request, f'Organizer {org.organization_name} rejected.')
    return redirect('manage_organizers')


# ------------------------------------------------
# 4. Organizer Home & Views
# ------------------------------------------------
@login_required
def organizer_dashboard(request):
    org = Organizer.objects.get(loginid=request.user)
    if org.status != 'approved':
        return render(request, 'organizer/pending_approval.html')
        
    events = Event.objects.filter(organizer=org)
    return render(request, 'organizer/dashboard.html', {'events': events, 'org': org})

@login_required
def create_event(request):
    org = Organizer.objects.get(loginid=request.user)
    
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
    event = get_object_or_404(Event, id=event_id)
    applications = Application.objects.filter(event=event)
    tasks = Task.objects.filter(event=event)
    
    return render(request, 'organizer/event_details.html', {
        'event': event, 
        'applications': applications, 
        'tasks': tasks
    })


# ------------------------------------------------
# 5. Volunteer Home & Views
# ------------------------------------------------
@login_required
def volunteer_dashboard(request):
    vol = Volunteer.objects.get(loginid=request.user)
    upcoming_events = Event.objects.filter(status='Upcoming')
    
    return render(request, 'volunteer/dashboard.html', {
        'events': upcoming_events, 
        'vol': vol
    })

@login_required
def apply_event(request, event_id):
    vol = Volunteer.objects.get(loginid=request.user)
    event = get_object_or_404(Event, id=event_id)
    
    if not Application.objects.filter(volunteer=vol, event=event).exists():
        Application.objects.create(volunteer=vol, event=event)
        messages.success(request, f'Successfully applied for {event.title}')
    else:
        messages.info(request, 'You have already applied for this event.')
        
    return redirect('volunteer_dashboard')

@login_required
def volunteer_profile(request):
    vol = Volunteer.objects.get(loginid=request.user)
    return render(request, 'volunteer/profile.html', {'vol': vol})
