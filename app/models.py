from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime
from taggit.managers import TaggableManager

# Create your models here.
class CustomUser(AbstractUser):
    # User information
    USER = (
        ('1', 'hoo'),
        ('2', 'officer'),
        ('3', 'member'),
        ('4', 'institution'),
    )
    user_type = models.CharField(choices=USER, max_length=25)
    profile_pic = models.ImageField(upload_to='profile_pic/')
    email = models.EmailField(max_length=150, unique=True)


class IT_Topics(models.Model): 
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
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
    
    STATUS_CHOICES = (
        (0,"Inactive"),
        (1,"Active"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    
    def __str__(self):
        return f"{self.sy_start.year}-{self.sy_end.year}"
    
class MemberType(models.Model):
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Tags(models.Model):
    name = models.CharField(max_length=50)
    
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
    

class Intetrested_Topics(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    topic = models.ForeignKey(IT_Topics, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.member.admin.first_name} - {self.topic.name}"

class Membership(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='members')
    membertype = models.ForeignKey(MemberType, on_delete=models.CASCADE, related_name='membertypes')
    school_year = models.ForeignKey(School_Year, on_delete=models.CASCADE)
    proof_of_payment = models.FileField(upload_to='payments/')
    payment_date = models.DateField(null=True, blank=True)

    # ✅ New status field with default = Pending
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text='Membership status: Pending (default), Approved, or Declined.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.member.admin.first_name} {self.member.admin.last_name} - {self.membertype.name} ({self.school_year})"

    



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
    available_slots = models.PositiveIntegerField(default=0)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    chair = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='chair_events',
        limit_choices_to={'user_type': 2}
    )
    co_chair = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='co_chair_events',
        limit_choices_to={'user_type': 2}
    )
    registration_link = models.URLField(blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    evaluation_link = models.URLField(blank=True, null=True)
    school_year = models.ForeignKey(School_Year, on_delete=models.CASCADE, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    tags = models.ForeignKey(Tags, on_delete=models.SET_NULL, null=True, blank=True)
    is_full = models.BooleanField(default=False)
    template_path = models.CharField(max_length=255, blank=True, null=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default='active',
        help_text='Set whether the event is active or inactive'
    )

    # def create_announcement(self, title, description, banner=None):
    #     """Create an announcement for this event.""
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
    



class Member_Event_Registration(models.Model):
    STATUS_CHOICES = [
        ('unregister', 'Unregister'),
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled'),
    ]

    member_id = models.ForeignKey(Member, on_delete=models.CASCADE, blank=True, null=True)           # Stores only the user ID
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)          # Stores only the event ID
    date_created = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unregister'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_present = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        try:
            member_username = getattr(self.member_id, 'admin', None) and getattr(self.member_id.admin, 'username', None)
            if member_username:
                return f"Registration of {member_username} for {self.event.title}"
        except Exception:
            pass
        return f"Registration {getattr(self, 'id', '')} for {getattr(self.event, 'title', '')}"

    
 
      
class Bulk_Event_Reg(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    registered_by = models.ForeignKey(Member,on_delete=models.CASCADE ,null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_name = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    middle = models.CharField(max_length=150, blank=True, null=True)
    contact_number = models.CharField(max_length=13)
    email = models.EmailField(max_length=150, blank=True, null=True)
    attending_as = models.CharField(max_length=100, blank=True, null=True)
    is_competitor = models.BooleanField(default=False)
    if_competitor = models.CharField(max_length=100, blank=True, null=True)
    is_coach = models.BooleanField(default=False)
    if_coach = models.CharField(max_length=100, blank=True, null=True)
    tshirt_size = models.CharField(max_length=10, blank=True, null=True)
    is_present = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
  
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"
    

class Event_Evaluation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=150, blank=True, null=True)
    q1_rating = models.IntegerField(blank=True, null=True)
    q2_rating = models.IntegerField(blank=True, null=True)
    q3_rating = models.IntegerField(blank=True, null=True)
    nps_rating = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Evaluation for {self.event.title} by {self.first_name} {self.last_name}"