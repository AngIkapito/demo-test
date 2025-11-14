from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.urls import path, include, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from app.models import CustomUser, Event, School_Year,Announcement, Salutation,Organization, MemberType, MembershipType, Member, OfficerType, Region, Membership, Member_Event_Registration
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import JsonResponse
import datetime
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.utils.crypto import get_random_string


@login_required(login_url='/')
def home(request):
    # Get the logged-in user
    user = request.user
    membership_expiry = None
    membership_status = None
    # Find the Member object for this user
    try:
        member = Member.objects.get(admin=user)
        # Get the latest approved membership for this member
        membership = (
            Membership.objects.filter(member=member, status='Approved')
            .select_related('school_year')
            .order_by('-school_year__sy_end')
            .first()
        )
        if membership and membership.school_year:
            membership_expiry = membership.school_year.sy_end
            membership_status = membership.school_year.status
    except Member.DoesNotExist:
        pass
    except Exception:
        pass

    context = {
        'user': user,
        'membership_expiry': membership_expiry,
        'membership_sy_status': membership_status,
    }
    return render(request, 'officer/home.html', context)



@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    
    context = {
        "user":user,

    }
    return render(request, 'officer/profile.html', context)


@login_required(login_url='/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        profile_pic = request.FILES.get('profile_pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        change_password = request.POST.get('change_password')  # renamed field

        try:
            customuser = CustomUser.objects.get(id=request.user.id)

            customuser.first_name = first_name
            customuser.last_name = last_name
            customuser.email = email
            customuser.username = username

            # If change password field is filled, update password
            if change_password and change_password.strip() != "":
                customuser.set_password(change_password)
                customuser.save()
                update_session_auth_hash(request, customuser)  # keep user logged in
            else:
                customuser.save()

            if profile_pic and profile_pic != "":
                customuser.profile_pic = profile_pic
                customuser.save()

            messages.success(request, 'Your profile was updated successfully!')
            return redirect('profile_update_officer')  # redirect to the same update page
        except Exception as e:
            print("Error updating profile:", e)  # for debugging
            messages.error(request, 'Failed to update your profile')
            return redirect('profile_update_officer')
    
    return render(request, 'officer/profile.html') 


def VIEWALL_EVENT(request):
    # Fetch all events with related school year to reduce queries
    events = Event.objects.select_related('school_year').all()
    return render(request, 'officer/viewall_event.html', {'events': events})





def MEMBER_EVENT_REG(request):
    """
    Handles the Member Event Registration form:
    - Displays active event details automatically.
    - Gets the logged-in user's ID.
    - Saves a registration to the Member_Event_Registration table.
    - Updates available_slots instead of modifying max_attendees.
    - Prevents duplicate registrations by the same user.
    - Shows a message when no active event exists.
    """
    # ✅ Fetch the active event (latest if multiple)
    event = Event.objects.filter(status='active').order_by('-date').first()

    # ✅ If no active event found
    if not event:
        messages.error(request, "There are currently no active events available for registration.")
        return render(request, 'officer/member_event_reg.html', {'event': None})

    if request.method == 'POST':
        user_id = request.user.id
        if not user_id:
            messages.error(request, "User not authenticated.")
            return redirect('member_event_reg')

        # ✅ Check for duplicate registration
        already_registered = Member_Event_Registration.objects.filter(
            user_id=user_id,
            event_id=event.id,
            status='registered'
        ).exists()

        if already_registered:
            messages.warning(request, "You are already registered for this event.")
            return redirect('member_event_reg')

        # ✅ Determine available slots (default to max_attendees if available_slots not set)
        available_slots = getattr(event, 'available_slots', event.max_attendees)

        if available_slots <= 0:
            if event.status != 'full':
                event.status = 'full'
                event.save(update_fields=['status'])
            messages.error(request, "Registration closed. The event is full.")
            return redirect('member_event_reg')

        try:
            # ✅ Create the registration record
            Member_Event_Registration.objects.create(
                user_id=user_id,
                event_id=event.id,
                date_created=timezone.now(),
                status='registered'
            )

            # ✅ Recalculate available slots: max_attendees - total registered
            total_registered = Member_Event_Registration.objects.filter(
                event_id=event.id, status='registered'
            ).count()
            new_available_slots = event.max_attendees - total_registered

            # ✅ Update event.available_slots and status
            event.available_slots = new_available_slots
            if new_available_slots <= 0:
                event.status = 'full'
            event.save(update_fields=['available_slots', 'status'])

            messages.success(request, "Registration successful!")
            return redirect('member_event_reg')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('member_event_reg')

    context = {'event': event}
    return render(request, 'officer/member_event_reg.html', context)


@login_required(login_url='/')
@require_http_methods(["GET", "POST"])
def MEMBERSHIP_APPROVAL(request):
    """
    View for Membership Registration Approval.
    GET: Fetch all members and map membership status.
    POST: Update membership status using membership.member_id for uniqueness.
    Sends emails using CustomUser email linked via Member.admin.
    """
    if request.method == "POST":
        # Use membership.member_id as unique identifier
        member_id = request.POST.get("member_id")
        action = request.POST.get("action")  # "approve" or "decline"

        # Find Member
        member = get_object_or_404(Member, id=member_id)
        # Get CustomUser details for name/email
        user = member.admin

        # Get related Membership
        # A member may have multiple Membership records (new + renew). Select the most
        # recent one to act upon. Prefer pending records if present; otherwise fall back
        # to the latest by id.
        membership_qs = Membership.objects.filter(member_id=member.id).order_by('-id')
        # Prefer a PENDING membership if one exists
        membership = membership_qs.filter(status__iexact='PENDING').first()
        if not membership:
            # Fall back to the latest membership record for this member
            membership = membership_qs.first()

        if not membership:
            messages.error(request, f"No membership record found for {user.first_name} {user.last_name}.")
            return redirect("membership_approval")

        if action == "approve":
            # Approve the membership record
            membership.status = "APPROVED"
            # record who processed this approval (store the id directly)
            try:
                membership.processed_by_id = getattr(request.user, 'id', None)
            except Exception:
                membership.processed_by_id = None
            membership.save()

            # Activate the user account
            user.is_active = 1
            user.save()

            # If this is a NEW membership (membertype != 2) generate credentials and email them.
            # For RENEWALS (membertype_id == 2) do NOT create a new password — just notify the user.
            if getattr(membership, 'membertype_id', None) != 2:
                # ✅ Generate new password for NEW registrations
                password = get_random_string(length=10)
                user.set_password(password)
                user.save()

                # ✅ Send approval email with username and password
                send_mail(
                    subject="Membership Approved",
                    message=(
                        f"Dear {user.first_name} {user.last_name},\n\n"
                        f"Your membership has been approved.\n"
                        f"Here are your login credentials:\n\n"
                        f"Username: {user.username}\n"
                        f"Password: {password}\n\n"
                        f"Please login and change your password as soon as possible."
                    ),
                    from_email="yourgmail@gmail.com",  # Replace with your EMAIL_HOST_USER
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f"Membership for {user.first_name} {user.last_name} approved, user activated, and email with credentials sent."
                )
            else:
                # Renewal: do not generate a new password. Send a simple approval notification.
                send_mail(
                    subject="Membership Renewal Approved",
                    message=(
                        f"Dear {user.first_name} {user.last_name},\n\n"
                        f"Your membership renewal has been approved.\n"
                        f"No changes were made to your login credentials.\n\n"
                        f"Thank you."
                    ),
                    from_email="yourgmail@gmail.com",  # Replace with your EMAIL_HOST_USER
                    recipient_list=[user.email],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f"Membership renewal for {user.first_name} {user.last_name} approved; user retains existing credentials."
                )

        elif action == "decline":
            membership.status = "DECLINED"
            # record who processed this decline (store the id directly)
            try:
                membership.processed_by_id = getattr(request.user, 'id', None)
            except Exception:
                membership.processed_by_id = None
            membership.save()

            processor_id = getattr(request.user, 'id', 'unknown')
            messages.warning(
                request,
                f"Membership for {user.first_name} {user.last_name} declined. Processed by id: {processor_id}"
            )
        else:
            messages.error(request, "Invalid action.")

        return redirect("membership_approval")

    # --- GET logic ---
    # Only consider memberships that are either NEW (membertype_id=1) or RENEW (membertype_id=2)
    memberships = (
        Membership.objects.filter(membertype_id__in=[1, 2])
        .order_by('-id')
        .only('member_id', 'status', 'proof_of_payment', 'membertype_id')
    )

    # Build maps using the latest membership per member (ordered by -id above)
    membership_status_map = {}
    membership_payment_map = {}
    membership_type_map = {}
    for m in memberships:
        if m.member_id not in membership_status_map:
            membership_status_map[m.member_id] = m.status
            membership_payment_map[m.member_id] = m.proof_of_payment
            membership_type_map[m.member_id] = getattr(m, 'membertype_id', None)

    # Get only members who have a relevant membership (new or renew)
    member_ids = list(membership_status_map.keys())
    members = Member.objects.select_related('admin', 'organization', 'membershiptype').filter(id__in=member_ids)

    # Add dynamic attributes for display using the maps
    for member in members:
        member.status = membership_status_map.get(member.id, 'PENDING')
        member.proof_of_payment = membership_payment_map.get(member.id, None)
        member.latest_membertype_id = membership_type_map.get(member.id)

    context = {
        'schoolyear': School_Year.objects.all(),
        'users': CustomUser.objects.all(),
        'members': members,
        'membership_status_map': membership_status_map,
        'memberships': memberships,
        'membership_types': MembershipType.objects.all(),
        'member_types': MemberType.objects.all(),
        'organization': Organization.objects.all(),
    }

    return render(request, 'officer/membership_approval.html', context)



