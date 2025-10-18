from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.urls import path, include, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import CustomUser, Event, School_Year,Announcement, Salutation,Organization, MemberType, MembershipType, Member, OfficerType, Region, Membership, Member_Event_Registration
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import JsonResponse
import datetime

@login_required(login_url='/')
def home(request):
    return render(request,'officer/home.html')



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




