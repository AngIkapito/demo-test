from django.shortcuts import render,redirect, HttpResponse
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from app.models import CustomUser, Member, Membership, Member_Event_Registration, Event, Tags
from django.utils import timezone
from django.utils.safestring import mark_safe
#from django.http import JsonResponse

@login_required(login_url='/')
def home(request):
    user = request.user
    membership_expiry = None
    membership_status = None
    try:
        member = Member.objects.get(admin=user)
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
    return render(request,'member/home.html', context)


@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    
    context = {
        "user":user,

    }
    return render(request, 'member/profile.html', context)

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
            return redirect('profile_update_member')  # redirect to the same update page
        except Exception as e:
            print("Error updating profile:", e)  # for debugging
            messages.error(request, 'Failed to update your profile')
            return redirect('profile_update_member')
    
    return render(request, 'member/profile.html') 


def basic_information(request):
    return render(request,'member/basic_information.html')




@login_required(login_url='/')
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
            return redirect('member_event_reg_member')

        # ✅ Check for duplicate registration
        already_registered = Member_Event_Registration.objects.filter(
            user_id=user_id,
            event_id=event.id,
            status='registered'
        ).exists()

        if already_registered:
            messages.warning(request, "You are already registered for this event.")
            return redirect('member_event_reg_member')

        # ✅ Determine available slots (default to max_attendees if available_slots not set)
        available_slots = getattr(event, 'available_slots', event.max_attendees)

        if available_slots <= 0:
            # mark the event as closed (1) when no slots remain; do NOT change status
            if getattr(event, 'is_closed', 0) != 1:
                try:
                    event.is_closed = 1
                    event.save(update_fields=['is_closed'])
                except Exception:
                    # silent fallback if `is_closed` doesn't exist
                    pass
            messages.error(request, "Registration closed. The event is full.")
            return redirect('member_event_reg_member')

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
            # Prevent negative available_slots which would cause DB errors
            if new_available_slots < 0:
                new_available_slots = 0

            # ✅ Update event.available_slots and is_closed flag (do NOT change status)
            event.available_slots = new_available_slots
            # set is_closed flag when no slots remain
            if new_available_slots <= 0:
                try:
                    event.is_closed = 1
                except Exception:
                    pass
            else:
                try:
                    event.is_closed = 0
                except Exception:
                    pass
            # try to save both fields; fall back to saving available_slots only
            try:
                event.save(update_fields=['available_slots', 'is_closed'])
            except Exception:
                event.save(update_fields=['available_slots'])

            messages.success(request, "Registration successful!")
            return redirect('member_event_reg_member')

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('member_event_reg_member')
    context = {'event': event}
    return render(request, 'member/member_event_reg.html', context)

