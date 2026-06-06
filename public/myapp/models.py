from django.db import models
from django.contrib.auth.models import AbstractUser

class Login(AbstractUser):
    # admin / organizer / volunteer
    userType = models.CharField(max_length=50)  
    viewPass = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Organizer(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    status = models.CharField(max_length=40, default="pending") # pending, approved, rejected

    def __str__(self):
        return self.organization_name

class Volunteer(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    skills = models.ManyToManyField(Skill, blank=True)
    interests = models.ManyToManyField(Category, blank=True)
    availability_status = models.CharField(max_length=50, default="available") # available, busy
    profile_pic = models.ImageField(upload_to="volunteer_profile", null=True, blank=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    required_skills = models.ManyToManyField(Skill, blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=300)
    max_volunteers = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.ManyToManyField(Skill, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.title} ({self.event.title})"

class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.volunteer.name} -> {self.event.title}"

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.volunteer.name} -> {self.task.title}"

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'volunteer')

    def __str__(self):
        return f"{self.volunteer.name} - {self.event.title} - Present: {self.is_present}"

class PerformanceReview(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(help_text="Rating out of 5", default=0)
    remarks = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'volunteer')

    def __str__(self):
        return f"{self.volunteer.name} - {self.event.title} - {self.rating}/5"

class Notification(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"
