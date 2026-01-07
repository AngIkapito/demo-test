from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, logout, login, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from app.models import Membership ,CustomUser, School_Year, Salutation, Member, MembershipType, MemberType, Announcement, OfficerType, Organization, Event, Tags, Member_Event_Registration, IT_Topics, Intetrested_Topics, Bulk_Event_Reg, Event_Evaluation
from django.utils.safestring import mark_safe
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import path, include, reverse
from django.utils.crypto import get_random_string
from datetime import datetime
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import random
import string
from django.db import transaction
from django.db.models import F
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

def REG_EVENT(request):
    """Render the registration page for a specific event.

    Expects `event_id` as a GET query parameter (from announcement links) or
    as a POST field when submitting the registration form.

    On GET: loads the Event and passes it to the template.
    On POST: validates requested seats against `event.available_slots` and
    shows a message (no persistent registration model implemented here).
    """
    # accept event id from GET or POST
    event_id = request.GET.get('event_id') or request.POST.get('event_id')
    if not event_id:
        messages.error(request, 'No event selected for registration.')
        return redirect('announcement')

    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        # Authenticate provided username/password (unless already logged in)
        if not request.user.is_authenticated:
            username = (request.POST.get('username') or '').strip()
            password = request.POST.get('password') or ''
            user = authenticate(request=request, username=username, password=password)
            if user is None:
                # Add an error to Django messages and re-render the page so it appears in the messages include
                messages.error(request, 'Invalid username or password. Please try again.')
                return render(request, 'registration_event.html', {'event': event})
        else:
            user = request.user

        # ---------- Membership active check ----------
        # Ensure the user has a Member record and an active Membership for the current school year (status=1)
        try:
            member_obj = Member.objects.filter(admin_id=user.id).first()
        except Exception:
            member_obj = None

        if not member_obj:
            messages.warning(request, 'No member profile found for this account. Please contact the administrator.')
            return render(request, 'registration_event.html', {'event': event})

        # Check for a Membership tied to this member with an active school year (status=1)
        has_active_membership = Membership.objects.filter(member_id=member_obj.id, school_year__status=1).exists()
        if not has_active_membership:
            # Inform the user their membership is expired and ask them to renew
            messages.warning(request, 'Your membership has expired. Please renew your membership to register for events.')
            return render(request, 'registration_event.html', {'event': event})
        # ---------- end membership check ----------

        # Single-seat registration (1 seat per submission). Decrement available_slots atomically.
        try:
            with transaction.atomic():
                # Lock the event row for update to avoid race conditions
                locked_event = Event.objects.select_for_update().get(id=event.id)

                # Prevent duplicate registrations (use Member instance rather than User.id)
                existing = Member_Event_Registration.objects.filter(member_id=member_obj, event_id=event.id, status='registered').exists()
                if existing:
                    messages.info(request, f'You are already registered for "{locked_event.title}".')
                    return redirect(reverse('registration_event') + f'?event_id={event.id}')

                # NOTE: removed decrement of `available_slots` per request — allow registrations
                reg = Member_Event_Registration.objects.create(
                    member_id=member_obj,
                    event_id=event.id,
                    status='registered'
                )

        except Event.DoesNotExist:
            messages.error(request, 'Event not found.')
            return redirect('announcement')
        except Exception as e:
            messages.error(request, f'Failed to save registration: {e}')
            return redirect(reverse('registration_event') + f'?event_id={event.id}')

        # Use POST-Redirect-GET to avoid duplicate submission on refresh.
        messages.success(request, 'Your registration is submitted. Please wait for approval.')
        return redirect(reverse('registration_event') + f'?event_id={event.id}')

    return render(request, 'registration_event.html', {'event': event})

def ANNOUNCEMENT(request):
    announcements = Announcement.objects.prefetch_related('tags').all()
    tags = Tags.objects.all()
    # All events to show on announcements page (most recent first).
    # We will show active, full, and inactive events; inactive ones are displayed faded in the template.
    active_events = Event.objects.all().order_by('-date')
    # Collect tags used by active events (Event.tags is a FK to Tags)
    active_tag_ids = [tid for tid in active_events.values_list('tags_id', flat=True) if tid]
    event_tags = Tags.objects.filter(id__in=active_tag_ids) if active_tag_ids else Tags.objects.none()
    query = request.GET.get('tags')

    if query:
        results = Tags.objects.filter(name__icontains=query)
    else:
        results = Tags.objects.all()
    
    # Get all announcements and order them by updated_at date, descending
    announcements = Announcement.objects.all().order_by('-updated_at')
    
    # Get the latest announcement   
    latest_announcement = announcements.first()  # This will be the latest announcement
    
    context = {
        'announcements': announcements,
        'tags': tags,
        'results': results,
        'latest_announcement': latest_announcement,
        'active_events': active_events,
        'event_tags': event_tags,
        # provide a simple range for templates that need 1..10
        'recommend_range': range(1, 11),
    }
    return render(request,'announcement.html', context)


def EVENT(request):
    return render(request,'event.html')

def LOGIN(request):
    # Pass through any `next` parameter so the login form can redirect after authentication
    next_url = request.GET.get('next', '')
    return render(request,'login.html', {'next': next_url})

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
        # support redirect after login
        next_url = request.POST.get('next') or request.GET.get('next')
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
            # If a next_url was provided and is safe, redirect there first
            if next_url:
                # Validate the URL is safe for redirection
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                    return redirect(next_url)

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
    # Log the user out (clears auth data) and ensure the session is fully flushed
    try:
        logout(request)
    except Exception:
        pass

    # Flush session data server-side and clear session cookie client-side
    try:
        request.session.flush()
    except Exception:
        try:
            request.session.clear()
        except Exception:
            pass

    response = redirect('homepage')
    try:
        # Delete the session cookie so the browser no longer sends it
        response.delete_cookie(settings.SESSION_COOKIE_NAME)
    except Exception:
        pass

    return response


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
    it_topics = IT_Topics.objects.all()

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
        # accept multiple selected IT topics
        it_topic_ids = request.POST.getlist('it_topic_id')

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

        # Save interested IT topics if provided (supports multiple selections, limit to 3)
        try:
            if it_topic_ids:
                # accept at most 3 topics; notify user if extras provided
                accepted_ids = [tid for tid in it_topic_ids if tid][:3]
                if len(it_topic_ids) > 3:
                    messages.warning(request, 'Only up to 3 IT topics are accepted; extras were ignored.')
                # bulk create using member_id and topic_id
                objs = [Intetrested_Topics(member_id=member.id, topic_id=tid) for tid in accepted_ids]
                if objs:
                    Intetrested_Topics.objects.bulk_create(objs)
        except Exception:
            # non-fatal: continue but log in future if needed
            pass

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
        'it_topics': it_topics,
    }

    return render(request, 'registration_new.html', context)

@login_required(login_url='/')
def REGISTRATION_RENEW(request):
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    memberships = Membership.objects.all()
    school_year = School_Year.objects.all()
    # latest_school_year kept for backward compatibility
    latest_school_year = School_Year.objects.latest('sy_start')
    # Get active school year id (if any)
    active_school_year = School_Year.objects.filter(status=1).first()
    active_school_year_id = active_school_year.id if active_school_year else None
    # Get the current member (if exists) for the logged-in user so the form can be pre-filled
    member = None
    latest_membership = None
    try:
        member = Member.objects.filter(admin=request.user).first()
        if member:
            latest_membership = Membership.objects.filter(member=member).order_by('-id').first()
    except Exception:
        member = None
        latest_membership = None
    
    if request.method == "POST":
        # If the logged-in user already has a Member record, treat this POST as a renewal.
        # Only payment-related fields will be accepted/updated for renewal.
        proof_of_payment = request.FILES.get('proof_of_payment')
        payment_date = request.POST.get('payment_date')
        # For renewals, always use the active school year (status=1)
        school_year_id = active_school_year_id

        if member:
            # Create a new Membership for renewal. As requested, set membertype_id = 2 for renewals.
            try:
                renewal = Membership(
                    member=member,
                    membertype_id=2,
                    school_year_id=school_year_id,
                    payment_date=payment_date,
                    proof_of_payment=proof_of_payment,
                )
                renewal.save()
                home_link = reverse('login')
                registration_message = (
                    f"{request.user.first_name} {request.user.last_name}, your renewal has been submitted.\n"
                    f"A staff member will verify your payment. <a href=\"{home_link}\">Go to Homepage</a>."
                )
                messages.success(request, mark_safe(registration_message))
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Failed to submit renewal: {e}')
                return redirect('registration_renew')

        # If no existing member, fall back to creating a new user/member (original behavior)
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
        
        proof_of_payment = proof_of_payment
        payment_date = payment_date
        
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
        'active_school_year_id': active_school_year_id,
        'member': member,
        'latest_membership': latest_membership,
    }
    
    return render(request, 'registration_renew.html', context)



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


@require_POST
def SUBMIT_RATING(request):
    """Accept a rating POST and save to Event_Evaluation if the email is registered

    Expected JSON or form POST fields: event_id, email, first_name, last_name, comments, rating
    Only accept if the Event is active and a Bulk_Event_Reg exists with the same email and event.
    """
    import json
    try:
        if request.content_type and 'application/json' in request.content_type:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        else:
            payload = request.POST

        event_id = payload.get('event_id') or payload.get('eventId')
        email = (payload.get('email') or '').strip()
        first_name = (payload.get('first_name') or payload.get('firstName') or '').strip()
        last_name = (payload.get('last_name') or payload.get('lastName') or '').strip()
        comments = payload.get('comments') or payload.get('comment') or payload.get('rateComment') or ''
        rating_raw = payload.get('rating') or payload.get('ratingValue')
        rating = int(rating_raw) if rating_raw not in (None, '') else 0
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Invalid payload: {e}'}, status=400)

    # Basic validation
    if not event_id or not email:
        return JsonResponse({'success': False, 'message': 'Missing event_id or email'}, status=400)

    # Ensure rating is in 1..5
    if not (1 <= rating <= 5):
        return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5'}, status=400)

    # Verify event exists and is active
    try:
        ev = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Event not found'}, status=404)

    if ev.status != 'active':
        return JsonResponse({'success': False, 'message': 'Event is not active'}, status=400)

    # Verify the email is registered for this event in Bulk_Event_Reg
    registered = Bulk_Event_Reg.objects.filter(event_id=ev.id, email__iexact=email).exists()
    if not registered:
        return JsonResponse({'success': False, 'message': 'Email not found for this event registration'}, status=403)

    # Prevent duplicate feedback: one submission per (event, email)
    already = Event_Evaluation.objects.filter(event=ev, email__iexact=email).exists()
    if already:
        return JsonResponse({'success': False, 'message': 'Feedback already submitted for this event with this email'}, status=409)

    # Save evaluation
    try:
        Event_Evaluation.objects.create(
            event=ev,
            rating=rating,
            comments=comments,
            last_name=last_name or None,
            first_name=first_name or None,
            email=email,
        )

        # Send a thank-you email to the submitter (do not fail the request on email errors)
        try:
            subject = f"Thank you for your feedback on {ev.title}"
            display_name = (first_name + ' ' + last_name).strip() if (first_name or last_name) else email
            body = (
                f"Hello {display_name},\n\n"
                f"Thank you for rating the event \"{ev.title}\". We received your rating of {rating} out of 5.\n\n"
                f"Your comments:\n{comments or '(no comments)'}\n\n"
                "We appreciate your feedback and will use it to improve future events.\n\n"
                "Regards,\n"
                f"{settings.DEFAULT_FROM_EMAIL}"
            )
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=True)
        except Exception:
            # Swallow email errors so user still receives feedback success
            pass
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Failed to save evaluation: {e}'}, status=500)

    return JsonResponse({'success': True, 'message': 'Thank you for your feedback'})