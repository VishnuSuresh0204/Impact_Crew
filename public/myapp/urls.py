from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/volunteer/', views.register_volunteer, name='register_volunteer'),
    path('register/organizer/', views.register_organizer, name='register_organizer'),
    
    # Admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_organizers/', views.manage_organizers, name='manage_organizers'),
    path('approve_organizer/<int:org_id>/', views.approve_organizer, name='approve_organizer'),
    path('reject_organizer/<int:org_id>/', views.reject_organizer, name='reject_organizer'),
    
    # Organizer
    path('organizer_dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('create_event/', views.create_event, name='create_event'),
    path('organizer/event/<int:event_id>/', views.organizer_event_details, name='organizer_event_details'),
    
    # Volunteer
    path('volunteer_dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('volunteer_profile/', views.volunteer_profile, name='volunteer_profile'),
    path('apply_event/<int:event_id>/', views.apply_event, name='apply_event'),
]
