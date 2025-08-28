from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime
from taggit.managers import TaggableManager

# Create your models here.
class CustomUser(AbstractUser):
    # User information
    USER = (
        (1, 'hoo'),
        (2, 'officer'),
        (3, 'member'),
    )
    user_type = models.CharField(choices=USER, max_length=25)
    profile_pic = models.ImageField(upload_to='profile_pic/')
    email = models.EmailField(max_length=150, unique=True)
    
class Salutation(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
        
class Region(models.Model):
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Organization(models.Model):
    initials = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='org_logo/')
    telephone = models.CharField(max_length=15, blank=True, null=True)  # New telephone field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class School_Year(models.Model):
    sy_start = models.DateField()
    sy_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sy_start.year}-{self.sy_end.year}"
    
class MemberType(models.Model):
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MembershipType(models.Model):
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class OfficerType(models.Model):
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
 
class Member(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    
    #Personal Information of Member
    middle_name = models.CharField(max_length=100,default="")
    
    contact_no = models.CharField(max_length=13,default="")
    birthdate = models.DateField(null=True, blank=True)
    gender =  models.CharField(max_length=6)
    
    #Membership Information
    officertype = models.ForeignKey(OfficerType, on_delete=models.CASCADE)
    membershiptype = models.ForeignKey(MembershipType, on_delete=models.CASCADE)
    # membertype = models.ForeignKey(MemberType, on_delete=models.CASCADE)
    salutation = models.ForeignKey(Salutation, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    position = models.CharField(max_length=50)
    facebook_profile_link = models.URLField(blank=True, null=True)
    terms_accepted = models.BooleanField(default=False, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.admin.first_name + " " + self.admin.last_name
    
class Membership(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='members')
    membertype = models.ForeignKey(MemberType, on_delete=models.CASCADE, related_name='membertypes')
    school_year = models.ForeignKey(School_Year, on_delete=models.CASCADE)
    proof_of_payment = models.FileField(upload_to='payments/')
    payment_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.admin.first_name} {self.member.admin.last_name} - {self.membership_type.name} ({self.school_year})"
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    theme = models.TextField()  # The theme of the event
    banner = models.ImageField(upload_to='eventbanner/', blank=True, null=True)  # New field for the event poster
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    max_attendees = models.PositiveIntegerField(default=0)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    chair = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name='chair_events', limit_choices_to={'user_type': 2})
    co_chair = models.ForeignKey(CustomUser , on_delete=models.CASCADE, related_name='co_chair_events', limit_choices_to={'user_type': 2})
    registration_link = models.URLField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    evaluation_link = models.URLField(blank=True, null=True)

    # def create_announcement(self, title, description, banner=None):
    #     """Create an announcement for this event."""
    #     announcement = Announcement.objects.create(
    #         title=title,
    #         description=description,
    #         banner=banner,  # Include the banner if provided
    #         created_by=self.created_by,  # Set the creator of the announcement to the event creator
    #         event=self  # Link the announcement to this event
    #     )
    #     return announcement

    def __str__(self):
        return self.title
    
class Announcement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()  # Changed to TextField for longer descriptions
    banner = models.ImageField(upload_to='announcementbanner/')  # Simplified upload path
    status = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)  # Change to SET_NULL
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)  # Link to Event
    tags = TaggableManager()
    
    def __str__(self):
        return self.title
    
# class EventRegistration(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_registrations')
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
#     registration_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=[('REGISTERED', 'REGISTERED'), ('CANCELLED', 'CANCELLED')], default='REGISTERED')
#     registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # New field for registration fee

#     def __str__(self):
#         return f"{self.user.username} - {self.event.title} ({self.status})"

class Test(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

    
  


    