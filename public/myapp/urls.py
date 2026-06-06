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
    path('admin_manage_volunteers/', views.admin_manage_volunteers, name='admin_manage_volunteers'),
    path('admin_toggle_volunteer/<int:vol_id>/', views.admin_toggle_volunteer, name='admin_toggle_volunteer'),
    path('admin_monitor_events/', views.admin_monitor_events, name='admin_monitor_events'),
    path('admin_manage_categories/', views.admin_manage_categories, name='admin_manage_categories'),
    path('admin_delete_category/<int:cat_id>/', views.admin_delete_category, name='admin_delete_category'),
    path('admin_manage_skills/', views.admin_manage_skills, name='admin_manage_skills'),
    path('admin_delete_skill/<int:skill_id>/', views.admin_delete_skill, name='admin_delete_skill'),
    path('admin_feedback/', views.admin_feedback, name='admin_feedback'),
    path('admin_report/', views.admin_report, name='admin_report'),
    
    # Organizer
    path('organizer_dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('create_event/', views.create_event, name='create_event'),
    path('organizer/event/<int:event_id>/', views.organizer_event_details, name='organizer_event_details'),
    path('organizer/application/<int:app_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('organizer/event/<int:event_id>/create_task/', views.create_task, name='create_task'),
    path('organizer/task/<int:task_id>/assign/', views.assign_task, name='assign_task'),
    path('organizer/event/<int:event_id>/attendance/', views.track_attendance, name='track_attendance'),
    path('organizer/event/<int:event_id>/evaluate/', views.evaluate_performance, name='evaluate_performance'),
    
    # Volunteer
    path('volunteer_dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('volunteer_profile/', views.volunteer_profile, name='volunteer_profile'),
    path('apply_event/<int:event_id>/', views.apply_event, name='apply_event'),
    path('volunteer/tasks/', views.volunteer_tasks, name='volunteer_tasks'),
    path('volunteer/task/<int:assignment_id>/update_status/', views.update_task_assignment_status, name='update_task_assignment_status'),
    path('volunteer/history/', views.volunteer_history, name='volunteer_history'),
    path('volunteer/certificate/<int:review_id>/', views.view_certificate, name='view_certificate'),

    # Feedback / Complaints
    path('feedback/', views.submit_feedback, name='submit_feedback'),
]
