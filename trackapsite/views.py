from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from app.models import Membership ,CustomUser, School_Year, Salutation, Member, MembershipType, MemberType, Announcement, OfficerType, Organization
from django.utils.safestring import mark_safe
from django.urls import path, include, reverse
from django.utils.crypto import get_random_string
from datetime import datetime
from taggit.models import Tag
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import random
import string
# Create your views here.




def BASE(request):
    current_year = datetime.now().year
    return render(request,'base.html',{'current_year': current_year})

def HOMEPAGE(request):
    return render(request,'home.html')

def ABOUT(request):
    return render(request,'about.html')

def CONTACT(request):
    return render(request,'contact.html')

def ANNOUNCEMENT(request):
    announcements = Announcement.objects.prefetch_related('tags').all()
    tags = Tag.objects.all()
    query = request.GET.get('tags')
    
    if query:
        results = Tag.objects.filter(tags__name__icontains=query)  # Adjust based on your model's tag field
    else:
        results = Tag.objects.all()  # Show all items if no query
    
    # Get all announcements and order them by updated_at date, descending
    announcements = Announcement.objects.all().order_by('-updated_at')
    
    # Get the latest announcement
    latest_announcement = announcements.first()  # This will be the latest announcement
    
    context = {
        'announcements': announcements, 
        'tags': tags, 
        'results': results, 
        'latest_announcement': latest_announcement
        }
    return render(request,'announcement.html', context)


def EVENT(request):
    return render(request,'event.html')

def LOGIN(request):
    return render(request,'login.html')

def ERRORPAGE(request):
    return render(request,'error_page.html')

def REGISTRATION(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the email is already taken
        if email and CustomUser .objects.filter(email=email).exists():
            messages.warning(request, 'Email is already taken')
            return redirect('registration')

        # Check if the username is already taken
        elif CustomUser .objects.filter(username=username).exists():
            messages.warning(request, 'Username is already taken')
            return redirect('registration')
        
        else:
            # Create a new user if email and username are unique
            user = CustomUser (
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                user_type=3,  # Adjust this based on your user type logic
            )
            
            user.set_password(password)  # Hash the password
            user.save()  # Save the user to the database
            # try:
            #     user.save()  # Save the user to the database
            #     # Prepare a success message with a login link
            login_link = reverse('login')  # Assuming 'login' is the name of your login URL pattern
            login_message = f'{user.first_name} {user.last_name} is successfully added. <a href="{login_link}">Click here to login.</a>'
            messages.success(request, mark_safe(login_message))
            # except Exception as e:
            #     messages.error(request, 'An error occurred while creating your account. Please try again.')
        return redirect('registration')

    return render(request, 'registration.html')  # Render the registration form if not a POST request

#feb282025
def doLogin(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')  # Get the value of the checkbox
        user = authenticate(request=request, username=username, password=password)

        if user is not None:
            login(request, user)
            user_type = user.user_type
            
            # Set session expiry based on "Remember Me" checkbox
            if remember_me:
                request.session.set_expiry(2592000)  # 30 days in seconds
            else:
                request.session.set_expiry(0)  # Session expires when the browser is closed

            # Redirect based on user type
            if user_type == '1':
                return redirect('hoo_home')
            elif user_type == '2':
                return redirect('officer_home')
            elif user_type == '3':
                return redirect('member_home')
            else:
                messages.error(request, 'Invalid user type.')
                return redirect('login')
        else:
            messages.error(request, 'Email and Password are Invalid, or Wait for the Admin to approve your Membership.')
            return redirect('login')
            
def doLogout(request):
    logout(request)
    return redirect('homepage')


@login_required(login_url='/')  
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    
    context = {
        "user":user,

    }
    return render(request, 'profile.html', context)


@login_required(login_url='/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
    # change_password = request.POST.get('change_password')  # removed password change functionality

        try:
            customuser = CustomUser.objects.get(id=request.user.id)

            customuser.first_name = first_name
            customuser.last_name = last_name

            # Password change functionality removed

            if profile_pic and profile_pic != "":
                customuser.profile_pic = profile_pic

            customuser.save()
            messages.success(request, 'Your profile was updated successfully!')
            return redirect('login')  # You may redirect to profile instead if needed
        except Exception as e:
            print("Error updating profile:", e)  # for debugging
            messages.error(request, 'Failed to update your profile')
    
    return render(request, 'login.html')




def PROFILE_PASSWORD_PAGE(request):
    user = CustomUser.objects.get(id = request.user.id)
    
    context = {
        "user":user,

    }
    return render(request, 'change_password.html', context)

@login_required(login_url='/')
def CHANGE_PASSWORD(request):
    if request.method == "POST":
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        repeat_new_password = request.POST.get('repeat_new_password')
        user = CustomUser.objects.get(id=request.user.id)

        # Check current password
        if not check_password(current_password, user.password):
            messages.error(request, "Current password is incorrect.")
            return redirect('change_password')

        # Check new password requirements
        errors = []
        if len(new_password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in new_password):
            errors.append("Password must contain at least one capital letter.")
        if not any(c.isdigit() for c in new_password):
            errors.append("Password must contain at least one number.")
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in new_password):
            errors.append("Password must contain at least one special character.")
        if new_password != repeat_new_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('change_password')

        # Set new password
        user.set_password(new_password)
        user.save()
        messages.success(request, "Your password has been changed successfully.")
        return redirect('login')

    return render(request, 'login.html')


# def REGISTRATION_BYPASS(request):
   
#     if request.method == "POST":
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         username = request.POST.get('username')
#         password = request.POST.get('password')
                      
#         if email and CustomUser.objects.filter(email=email).exists():
#              messages.warning(request,'Email is already taken')
#              return redirect('registration')
#         elif CustomUser.objects.filter(username=username).exists():
#              messages.warning(request,'Username is already taken')
#              return redirect('registration')     
#         else:
#             user = CustomUser(
#                 first_name = first_name,
#                 last_name = last_name,
#                 username = username,
#                 email = email if email else None,
#                 user_type = 3,
#                 )        
#             user.set_password(password)
#             user.save()
            
#             login_link = reverse('login')  # Assuming 'login' is the name of your login URL pattern
#             login_message = f'{user.first_name} {user.last_name} is successfully added. <a href="{login_link}">Click here to login.</a>'
#             messages.success(request, mark_safe(login_message))
#             return redirect('registration_bypass')
    
#     return render(request, 'registration_bypass.html')

# Pagamit ito sa mga SSITE officer para mag add ng mga members sa 
# System using trackapsite.com/registration_bypass1/


def REGISTRATION_NEW(request):
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    memberships = Membership.objects.all()
    school_year = School_Year.objects.all()

    # ✅ Get active School Year
    active_school_year = get_object_or_404(School_Year, status=1)
    active_school_year_id = active_school_year.id

    if request.method == "POST":
        # ✅ Safely get and normalize form values
        first_name = (request.POST.get('first_name') or '').strip().upper()
        last_name = (request.POST.get('last_name') or '').strip().upper()
        middle_name = (request.POST.get('middle_name') or '').strip().upper()
        email = (request.POST.get('email') or '').strip().lower()
        username = (request.POST.get('username') or '').strip()  # Get from HTML
        membershiptype_id = request.POST.get('membershiptype_id')
        membertype_id = request.POST.get('membertype_id')
        organization_id = request.POST.get('organization_id')
        salutation_id = request.POST.get('salutation_id')
        officertype_id = request.POST.get('officertype_id')
        school_year_id = request.POST.get('school_year_id')
        position = (request.POST.get('position') or '').strip().upper()
        contact_no = (request.POST.get('contact_no') or '').strip()
        birthdate = request.POST.get('birthdate')
        facebook_profile_link = (request.POST.get('facebook_profile_link') or '').strip()

        proof_of_payment = request.FILES.get('proof_of_payment')
        payment_date = request.POST.get('payment_date')

        # Terms checkbox
        terms_accepted = request.POST.get('terms_accepted') == 'true' or request.POST.get('terms_accepted') == 'on'

        # ✅ Ensure submitted school_year_id corresponds to an active school year
        school_year_instance = get_object_or_404(School_Year, id=school_year_id, status=1)

        # ✅ Validate required fields
        if not first_name or not last_name or not email or not username:
            messages.error(request, 'First name, last name, email, and username are required.')
            return redirect('registration_new')

        # ✅ Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email is already registered.')
            return redirect('registration_new')

        # ✅ Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists. Please modify your first/last name to generate a new one.')
            return redirect('registration_new')

        # ✅ Auto-generate a password
        password = get_random_string(length=10)

        # ✅ Create CustomUser
        user = CustomUser(
            is_superuser=0,
            is_active=0,
            user_type=3,
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
        )
        user.set_password(password)
        user.save()

        # ✅ Create Member
        member = Member(
            admin=user,
            membershiptype_id=membershiptype_id,
            officertype_id=officertype_id,
            organization_id=organization_id,
            salutation_id=salutation_id,
            middle_name=middle_name,
            birthdate=birthdate,
            position=position,
            contact_no=contact_no,
            facebook_profile_link=facebook_profile_link,
            terms_accepted=terms_accepted,
        )
        member.save()

        # ✅ Create Membership
        membership = Membership(
            member=member,
            membertype_id=membertype_id,
            school_year_id=school_year_id,
            payment_date=payment_date,
            proof_of_payment=proof_of_payment,
        )
        membership.save()

        # ✅ Confirmation message
        home_link = reverse('login')
        registration_message = (
            f"{user.first_name} {user.last_name}, kindly wait for membership verification.<br>"
            f"Your login credentials (Username: <b>{username}</b>) will be emailed after approval.<br>"
            f'<a href="{home_link}">Click here to go to Homepage.</a>'
        )
        messages.success(request, mark_safe(registration_message))
        return redirect('login')

    context = {
        'salutations': salutations,
        'membershiptypes': membershiptypes,
        'membertypes': membertypes,
        'officertypes': officertypes,
        'organizations': organizations,
        'memberships': memberships,
        'school_year': school_year,
        'active_school_year_id': active_school_year_id,
    }

    return render(request, 'registration_new.html', context)

def REGISTRATION_RENEW(request):
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    memberships = Membership.objects.all()
    school_year = School_Year.objects.all()
    latest_school_year = School_Year.objects.latest('sy_start')
    
    if request.method == "POST":
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        email = request.POST.get('email').strip().lower()
        username = request.POST.get('username').strip().lower()
        membershiptype_id = request.POST.get('membershiptype_id')
        membertype_id = request.POST.get('membertype_id')
        organization_id = request.POST.get('organization_id')
        salutation_id = request.POST.get('salutation_id')
        officertype_id = request.POST.get('officertype_id')
        school_year_id = request.POST.get('school_year_id')
        
        middle_name = request.POST.get('middle_name').upper()
        position = request.POST.get('position').upper()
        contact_no = request.POST.get('contact_no')
        birthdate = request.POST.get('birthdate')
        facebook_profile_link = request.POST.get('facebook_profile_link')
        
        proof_of_payment = request.FILES.get('proof_of_payment')
        payment_date = request.POST.get('payment_date')
        
        terms_accepted = request.POST.get('terms_accepted') == 'true'
        password = request.POST.get('password')
        
        # password = f"{first_name[:2]}{last_name[-2:]}{birth_year[-2:]}"  # Example: Joith90
        
        # Check if email already exists
        if email and CustomUser .objects.filter(email=email).exists():
            messages.warning(request, 'Email is already taken')
            return redirect('registration_new')
        
        else:
            
        # Create the CustomUser instance
            user = CustomUser (
                is_superuser=0,
                is_active=0,
                user_type=3,
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            
            user.set_password(password)
            user.save()
            
            # Create the Member instance
            member = Member (
                admin=user,
                membershiptype_id=membershiptype_id,
                officertype_id=officertype_id,
                organization_id=organization_id,
                salutation_id=salutation_id,
                middle_name=middle_name,
                birthdate=birthdate,
                position=position,
                contact_no=contact_no,
                facebook_profile_link=facebook_profile_link,
                terms_accepted=terms_accepted,
            )
            member.save()
            
            # Retrieve the MemberType instance
            # member_type_instance = get_object_or_404(MemberType, id=membertype_id)
        
            # Create the Membership instance
            membership = Membership(
                member=member,  # Link to the Member instance
                membertype_id=membertype_id,  # Use the MemberType instance
                school_year_id=school_year_id,
                payment_date=payment_date,
                proof_of_payment=proof_of_payment,
            )
            membership.save()
            
        home_link = reverse('login')
        registration_message = f'{user.first_name} {user.last_name}. Kindly wait for the verification of your Membership. <br>Your default credentials will be sent via your Email. <a href="{home_link}">Click here to go to Homepage.</a>'
        messages.success(request, mark_safe(registration_message))
        return redirect('login')
    
    context = {
        'salutations': salutations,
        'membershiptypes': membershiptypes,
        'membertypes': membertypes,
        'officertypes': officertypes,
        'organizations': organizations,
        'memberships': memberships,
        'school_year': school_year,
        'latest_school_year': latest_school_year,
    }
    
    return render(request, 'registration_new.html', context)



User = get_user_model()

def FORGOT_PASSWORD(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            # Generate a random new password
            new_password = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )

            # Set and save new password (hashed)
            user.set_password(new_password)
            user.save()

            # Send the new password to the user’s email
            send_mail(
                "Your New Password",
                f"Hello {user.username},\n\nYour new password is: {new_password}\n\n"
                f"Please log in and change it immediately.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )

        except User.DoesNotExist:
            # Do nothing if user not found (don’t expose info)
            pass

        return render(request, "forgot_password_done.html")

    return render(request, "forgot_password.html")