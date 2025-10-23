from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.urls import path, include, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from app.models import CustomUser, Event, School_Year,Announcement, Salutation,Organization, MemberType, MembershipType, Member, OfficerType, Region, Membership, Member_Event_Registration
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
import datetime

# Create your views here.
@login_required(login_url='/')
def home(request):
    # Get all members and events
    members = Member.objects.all()
    events = Event.objects.all()

    # Fetch the latest active event for the progress bar
    event = Event.objects.filter(status='active').order_by('-date').first()

    if event:
        # Calculate the number of registered members for this event
        registered_count = Member_Event_Registration.objects.filter(
            event_id=event.id,
            status='registered'
        ).count()

        # Calculate available slots
        available_slots = max(event.max_attendees - registered_count, 0)

        # Calculate percentage for progress bar
        progress_percent = (registered_count / event.max_attendees) * 100 if event.max_attendees else 0
    else:
        # No active event
        registered_count = 0
        available_slots = 0
        progress_percent = 0

    context = {
        'members': members,
        'events': events,
        'event': event,
        'registered_count': registered_count,
        'available_slots': available_slots,
        'progress_percent': progress_percent,  # pass percentage
    }

    return render(request, 'hoo/home.html', context)


#for the profile
@login_required(login_url='/')
def PROFILE(request):
    user = CustomUser.objects.get(id = request.user.id)
    
    context = {
        "user":user,

    }
    return render(request, 'hoo/profile.html', context)



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
            return redirect('profile_update_hoo')  # redirect to the same update page
        except Exception as e:
            print("Error updating profile:", e)  # for debugging
            messages.error(request, 'Failed to update your profile')
            return redirect('profile_update_hoo')
    
    return render(request, 'hoo/profile.html')  # use your correct template



# For Schoolyear 
def ADD_SCHOOLYEAR(request):
    if request.method == "POST":
        sy_start = request.POST.get('sy_start')
        sy_end = request.POST.get('sy_end')

        # Deactivate all existing school years
        School_Year.objects.update(status=0)

        # Create the new one as active
        school_year = School_Year(
            sy_start=sy_start,
            sy_end=sy_end,
            status=1,  # auto set active
        )
        school_year.save()

        messages.success(request, 'Cycle successfully added and set as Active!')
        return redirect('add_schoolyear')

    return render(request, 'hoo/add_schoolyear.html')

def VIEW_SCHOOLYEAR(request):
    schoolyear = School_Year.objects.all()
    
    context = {
        'schoolyear':schoolyear,
    }
    # print(teacher)
    return render(request, 'hoo/view_schoolyear.html', context)


def EDIT_SCHOOLYEAR(request, id):
    schoolyear = School_Year.objects.filter(id = id)
    
    context = {
        'schoolyear':schoolyear
    }
    
    return render(request,'hoo/edit_schoolyear.html', context)


def UPDATE_SCHOOLYEAR(request):
    if request.method == "POST":
        id = request.POST.get('id')
        sy_start = request.POST.get('sy_start')
        sy_end = request.POST.get('sy_end')
        # print(program)
        
        schoolyear = School_Year.objects.get(id = id)
        schoolyear.sy_start = sy_start
        schoolyear.sy_end = sy_end
        
        schoolyear.save()
        
        messages.success(request, "Cycle successfully updated")
        return redirect('view_schoolyear')
    return render(request, 'hoo/edit_schoolyear.html')

def DELETE_SCHOOLYEAR(request, id):
    schoolyear = School_Year.objects.get(id = id)
    schoolyear.delete()
    messages.success(request, 'Cycle successfully deleted')
    return redirect('view_schoolyear')

# For Member List
def ADD_MEMBER(request):
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    # membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    # customuser = CustomUser.objects.all()
    
    if request.method == "POST":
        # is_superuser = request.POST.get('is_superuser')
        # is_active = request.POST.get('is_active')
        # user_type = request.POST.get('user_type')
        
        membershiptype_id = request.POST.get('membershiptype_id')
        # membertype_id = request.POST.get('membertype_id')
        organization_id = request.POST.get('organization_id')
        
        salutation_id = request.POST.get('salutation_id')
        officertype_id = request.POST.get('officertype_id')
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        middle_name = request.POST.get('middle_name').upper()
        # profile_pic = request.FILES.get('profile_pic')
        position = request.POST.get('position').upper()
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')
        birthdate = request.POST.get('birthdate')
        
        # Get the birthdate and convert it to a date object
        birthdate_str = request.POST.get('birthdate')
        birthdate = None
        if birthdate_str:
            try:
                birthdate = datetime.datetime.strptime(birthdate_str, '%Y-%m-%d').date()
            except ValueError:
                messages.warning(request, 'Invalid birthdate format. Please use YYYY-MM-DD.')
                return redirect('add_member')
        
        facebook_profile_link = request.POST.get('facebook_profile_link')
        # proof_of_payment = request.FILES.get('proof_of_payment')
        payment_date = request.POST.get('payment_date')
        terms_accepted = request.POST.get('terms_accepted') == 'true'
        
        username = request.POST.get('username')
        password = request.POST.get('password')
                 
        print(f"Checking email: {email}, Exists: {CustomUser .objects.filter(email=email).exists()}")              
        if email and CustomUser.objects.filter(email=email).exists():
             messages.warning(request,'Email is already taken')
             return redirect('add_member')
         
        elif CustomUser.objects.filter(username=username).exists():
             messages.warning(request,'Username is already taken')
             return redirect('add_member')     
         
        else:
            user = CustomUser(
                # is_superuser = is_superuser,
                # is_active = is_active,
                first_name = first_name,
                last_name = last_name,
                username = username,
                email = email,
                user_type = 3,
                # profile_pic = profile_pic,
                )      
              
            user.set_password(password)
            user.save()
            
            member = Member(
                admin = user, 
                membershiptype_id = membershiptype_id,
                # membertype_id = membertype_id,
                officertype_id = officertype_id,
                organization_id = organization_id,
                
                salutation_id = salutation_id,
                middle_name = middle_name,
                birthdate = birthdate,
                position = position,
                contact_no = contact_no,
                facebook_profile_link = facebook_profile_link,
                payment_date = payment_date,
                # proof_of_payment = proof_of_payment,
                terms_accepted = terms_accepted,
            )
            
            # member.set_password(password)
            member.save()
            
            messages.success(request,user.first_name + " " + user.last_name + " is successfully added")
            return redirect('add_member')
    
    context = {
        'salutations': salutations,  # Pass the salutations to the template
        'membershiptypes':membershiptypes,
        # 'membertypes': membertypes,
        'officertypes': officertypes,
        'organizations': organizations,
    }
    
    return render(request, 'hoo/add_member.html', context)

def VIEWALL_MEMBER(request):
    # customuser = request.user
    customuser = CustomUser.objects.all()
    members = Member.objects.all()
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    # membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    
    context = {
        'customuser':customuser,
        'members':members,
        'salutations': salutations,  # Pass the salutations to the template
        'membershiptypes':membershiptypes,
        # 'membertypes': membertypes,
        'officertypes': officertypes,
        'organizations': organizations,
    }
    # print(customuser)
    return render(request, 'hoo/viewall_member.html', context)

def EDIT_MEMBER(request, id):
    salutations = Salutation.objects.all()
    membershiptypes = MembershipType.objects.all()
    # membertypes = MemberType.objects.all()
    officertypes = OfficerType.objects.all()
    organizations = Organization.objects.all()
    
    member = get_object_or_404(Member, id=id)

    # selected_user =   # Assuming 'admin' is a ForeignKey to CustomUser 
    
    context = {
        # 'selected_user': selected_user,  # Pass the selected user to the template
        'member': member,
        'salutations': salutations,  # Pass the salutations to the template
        'membershiptypes': membershiptypes,
        # 'membertypes': membertypes,
        'officertypes': officertypes,
        'organizations': organizations,
    }
    
    return render(request, 'hoo/edit_member.html', context)

def UPDATE_MEMBER(request):
    if request.method == "POST":
        member_id = request.POST.get('member_id')
        is_superuser = request.POST.get('is_superuser') == 'on'  # Convert to boolean
        is_active = request.POST.get('is_active')      # Convert to boolean
        user_type = request.POST.get('user_type')
        
        membership_type = request.POST.get('membership_type')
        # member_type = request.POST.get('member_type')
        
        salutation = request.POST.get('salutation')
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        middle_name = request.POST.get('middle_name').upper()
        profile_pic = request.FILES.get('profile_pic')
        position = request.POST.get('position').upper()
        email = request.POST.get('email')
        contact_no = request.POST.get('contact_no')
        birthdate = request.POST.get('birthdate')
        facebook_profile_link = request.POST.get('facebook_profile_link')
        # proof_of_payment = request.FILES.get('proof_of_payment')
        payment_date = request.POST.get('payment_date')
        terms_accepted = request.POST.get('terms_accepted')
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        # print(program)
        
        customuser = CustomUser.objects.get(id = member_id)
        # customuser = get_object_or_404(CustomUser , id=member_id)
        
        
        # customuser.id = member_id
        customuser.is_superuser = is_superuser
        customuser.is_active = is_active
        customuser.user_type = user_type
        
        customuser.membership_type = membership_type
        # customuser.member_type = 1
        
        customuser.salutation = salutation
        customuser.first_name = first_name
        customuser.last_name = last_name
        customuser.middle_name = middle_name
        customuser.profile_pic = profile_pic
        customuser.position = position
        customuser.email = email
        customuser.contact_no = contact_no
        customuser.birthdate = birthdate
        customuser.facebook_profile_link = facebook_profile_link
        customuser.payment_date = payment_date
        customuser.terms_accepted = terms_accepted
        
        customuser.username = username
        customuser.password = password
        
        
        # Retrieve the user object or return a 404 error if not found
        
        if password !=None and password != "":
            customuser.set_password(password)
            
        customuser.save()
        
        messages.success(request, "Member successfully updated")
        return redirect('viewall_member')
    return render(request, 'hoo/edit_member.html')

def DELETE_MEMBER(request, id):
    customuser = CustomUser.objects.get(id = id)
    customuser.delete()
    messages.success(request, 'Member successfully deleted')
    return redirect('viewall_member')

def MEMBER_DETAILS(request,id):
    selected_member = Member.objects.filter(id = id)
    member= Member.objects.get(id=id)
    
    context = {
        'member':member,
        'selected_member':selected_member,
   
    }
    return render(request, 'hoo/member_details.html', context)

#For Region/Chapter Modules
def VIEW_REGION(request):
    region = Region.objects.all()
    
    context = {
        'region':region,
    }
    # print(teacher)
    return render(request, 'hoo/view_region.html', context)

def ADD_REGION(request):
    if request.method == "POST":
        region_name = request.POST.get('region_name')
        region_info = request.POST.get('region_info')
        # print(program_name)
        
        region = Region (
            name = region_name,
            info = region_info,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        region.save()
        messages.success(request, 'Region/Chapter successfully added!')
        return redirect('add_region')
    return render(request, 'hoo/add_region.html')

def EDIT_REGION(request, id):
    region = Region.objects.filter(id = id)
    
    context = {
        'region':region,
    }
    
    return render(request,'hoo/edit_region.html', context)

def UPDATE_REGION(request):
    if request.method == "POST":
        id = request.POST.get('region_id')
        region_name = request.POST.get('region_name')
        region_info = request.POST.get('region_info')
        # print(program)
        
        region = Region.objects.get(id = id)
        region.name = region_name
        region.info = region_info
        
        region.save()
        
        messages.success(request, "Region/Chapter successfully updated")
        return redirect('view_region')
    return render(request, 'hoo/edit_region.html')

def DELETE_REGION(request, id):
    region = Region.objects.get(id = id)
    region.delete()
    messages.success(request, 'Region/Chapter successfully deleted')
    return redirect('view_region')

#For Officertypes Modules
def VIEW_OFFICERTYPE(request):
    officertype = OfficerType.objects.all()
    
    context = {
        'officertype':officertype,
    }
    # print(teacher)
    return render(request, 'hoo/view_officertype.html', context)

def ADD_OFFICERTYPE(request):
    if request.method == "POST":
        officertype_name = request.POST.get('officertype_name')
        officertype_info = request.POST.get('officertype_info')
        # print(program_name)
        
        officertype = OfficerType (
            name = officertype_name,
            info = officertype_info,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        officertype.save()
        messages.success(request, 'OfficerType successfully added!')
        return redirect('add_officertype')
    return render(request, 'hoo/add_officertype.html')

def DELETE_OFFICERTYPE(request, id):
    officertype = OfficerType.objects.get(id = id)
    officertype.delete()
    messages.success(request, 'OfficerType successfully deleted')
    return redirect('view_officertype')

def EDIT_OFFICERTYPE(request, id):
    officertype = OfficerType.objects.filter(id = id)
    
    context = {
        'officertype':officertype,
    }
    
    return render(request,'hoo/edit_officertype.html', context)

def UPDATE_OFFICERTYPE(request):
    if request.method == "POST":
        id = request.POST.get('officertype_id')
        officertype_name = request.POST.get('officertype_name')
        officertype_info = request.POST.get('officertype_info')
        # print(program)
        
        officertype = OfficerType.objects.get(id = id)
        officertype.name = officertype_name
        officertype.info = officertype_info
        
        officertype.save()
        
        messages.success(request, "OfficerType successfully updated")
        return redirect('view_officertype')
    return render(request, 'hoo/edit_officertype.html')

#For Membership Modules
def VIEW_MEMBERSHIPTYPE(request):
    membershiptype = MembershipType.objects.all()
    
    context = {
        'membershiptype':membershiptype,
    }
    # print(teacher)
    return render(request, 'hoo/view_membershiptype.html', context)

def ADD_MEMBERSHIPTYPE(request):
    if request.method == "POST":
        membershiptype_name = request.POST.get('membershiptype_name')
        membershiptype_info = request.POST.get('membershiptype_info')
        membershiptype_price = request.POST.get('membershiptype_price')
        # print(program_name)
        
        membershiptype = MembershipType (
            name = membershiptype_name,
            info = membershiptype_info,
            price = membershiptype_price,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        membershiptype.save()
        messages.success(request, 'MembershipType successfully added!')
        return redirect('view_membershiptype')
    return render(request, 'hoo/add_membershiptype.html')

def DELETE_MEMBERSHIPTYPE(request, id):
    membershiptype = MembershipType.objects.get(id = id)
    membershiptype.delete()
    messages.success(request, 'MembershipType successfully deleted')
    return redirect('view_membershiptype')

def EDIT_MEMBERSHIPTYPE(request, id):
    membershiptype = MembershipType.objects.filter(id = id)
    
    context = {
        'membershiptype':membershiptype,
    }
    
    return render(request,'hoo/edit_membershiptype.html', context)

def UPDATE_MEMBERSHIPTYPE(request):
    if request.method == "POST":
        id = request.POST.get('membershiptype_id')
        membershiptype_name = request.POST.get('membershiptype_name')
        membershiptype_info = request.POST.get('membershiptype_info')
        membershiptype_price = request.POST.get('membershiptype_price')
        # print(program)
        
        membershiptype = MembershipType.objects.get(id = id)
        membershiptype.name = membershiptype_name
        membershiptype.info = membershiptype_info
        membershiptype.price = membershiptype_price
        
        membershiptype.save()
        
        messages.success(request, "MembershipType successfully updated")
        return redirect('view_membershiptype')
    return render(request, 'hoo/edit_membershiptype.html')


#For Membertype Modules
def VIEW_MEMBERTYPE(request):
    membertype = MemberType.objects.all()
    
    context = {
        'membertype':membertype,
    }
    # print(teacher)
    return render(request, 'hoo/view_membertype.html', context)

def ADD_MEMBERTYPE(request):
    if request.method == "POST":
        membertype_name = request.POST.get('membertype_name')
        membertype_info = request.POST.get('membertype_info')
        # print(program_name)
        
        membertype = MemberType (
            name = membertype_name,
            info = membertype_info,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        membertype.save()
        messages.success(request, 'MemberType successfully added!')
        return redirect('view_membertype')
    return render(request, 'hoo/add_membertype.html')

def DELETE_MEMBERTYPE(request, id):
    membertype = MemberType.objects.get(id = id)
    membertype.delete()
    messages.success(request, 'MemberType successfully deleted')
    return redirect('view_membertype')

def EDIT_MEMBERTYPE(request, id):
    membertype = MemberType.objects.filter(id = id)
    
    context = {
        'membertype':membertype,
    }
    
    return render(request,'hoo/edit_membertype.html', context)

def UPDATE_MEMBERTYPE(request):
    if request.method == "POST":
        id = request.POST.get('membertype_id')
        membertype_name = request.POST.get('membertype_name')
        membertype_info = request.POST.get('membertype_info')
        # print(program)
        
        membertype = MemberType.objects.get(id = id)
        membertype.name = membertype_name
        membertype.info = membertype_info
        
        membertype.save()
        
        messages.success(request, "MemberType successfully updated")
        return redirect('view_membertype')
    return render(request, 'hoo/edit_membertype.html')

#For Organization Modules
def VIEW_ORGANIZATION(request):
    organization = Organization.objects.all()
    
    context = {
        'organization':organization,
    }
    # print(teacher)
    return render(request, 'hoo/view_organization.html', context)

def ADD_ORGANIZATION(request):
    if request.method == "POST":
        organization_initials = request.POST.get('organization_initials')
        organization_name = request.POST.get('organization_name')
        organization_type = request.POST.get('organization_type')
        organization_logo = request.FILES.get('organization_logo')
        organization_telno = request.POST.get('organization_telno')
        # print(program_name)
        
        organization = Organization (
            initials = organization_initials,
            name = organization_name,
            type = organization_type,
            logo = organization_logo,
            telephone = organization_telno,
            # created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        organization.save()
        messages.success(request, 'Organization successfully added!')
        return redirect('view_organization')
    return render(request, 'hoo/add_organization.html')

def DELETE_ORGANIZATION(request, id):
    organization = Organization.objects.get(id = id)
    organization.delete()
    messages.success(request, 'Organization successfully deleted')
    return redirect('view_organization')

def EDIT_ORGANIZATION(request, id):
    organization = Organization.objects.filter(id = id)
    organizations = Organization.objects.all()
    
    context = {
        'organization':organization,
        'organizations':organizations,
    }
    
    return render(request,'hoo/edit_organization.html', context)

def UPDATE_ORGANIZATION(request):
    if request.method == "POST":
        id = request.POST.get('organization_id')
        organization_initials = request.POST.get('organization_initials')
        organization_name = request.POST.get('organization_name')
        organization_type = request.POST.get('organization_type')
        organization_logo = request.FILES.get('organization_logo')
        organization_telno = request.POST.get('organization_telno')
        # print(program)
        
        organization = Organization.objects.get(id = id)
        organization.initials = organization_initials
        organization.name = organization_name
        organization.type = organization_type
        organization.logo = organization_logo
        organization.telephone = organization_telno
        
        organization.save()
        
        messages.success(request, "Organization successfully updated")
        return redirect('view_organization')
    return render(request, 'hoo/edit_organization.html')

#For Announcement Modules
def VIEW_ANNOUNCEMENT(request):
    announcements = Announcement.objects.all()
    
    context = {
        'announcements':announcements,
    }
    # print(teacher)
    return render(request, 'hoo/view_announcement.html', context)

def ADD_ANNOUNCEMENT(request):
    if request.method == "POST":
        announcement_title = request.POST.get('announcement_title')
        announcement_description = request.POST.get('announcement_description')
        announcement_banner = request.FILES.get('announcement_banner')
        announcement_status = request.POST.get('announcement_status')
        announcement_tags = request.POST.get('announcement_tags')
        # print(program_name)
        
        announcement = Announcement (
            title = announcement_title,
            description = announcement_description,
            banner = announcement_banner,
            status = announcement_status,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        announcement.save()
        
        # Handle tags
        if announcement_tags:
            tags_list = [tag.strip() for tag in announcement_tags.split(',')]
            announcement.tags.add(*tags_list)  # Add tags to the announcement
        
        
        messages.success(request, 'Announcement successfully added!')
        return redirect('view_announcement')
    return render(request, 'hoo/add_announcement.html')

def DELETE_ANNOUNCEMENT(request, id):
    announcement = Announcement.objects.get(id = id)
    announcement.delete()
    messages.success(request, 'Announcement successfully deleted')
    return redirect('view_announcement')

def EDIT_ANNOUNCEMENT(request, id):
    announcement = Announcement.objects.filter(id = id)
    announcements = Announcement.objects.all()
    # tags_string = ', '.join([str(tag) for tag in announcement.tags.all()])
    
    context = {
        'announcement':announcement,
        'announcements':announcements,
        # 'tags_string': tags_string,  # Pass the tags string to the template
    }

    return render(request,'hoo/edit_announcement.html', context)

def UPDATE_ANNOUNCEMENT(request):
    if request.method == "POST":
        id = request.POST.get('announcement_id')
        announcement_title = request.POST.get('announcement_title')
        announcement_description = request.POST.get('announcement_description')
        announcement_banner = request.FILES.get('announcement_banner')
        announcement_status = request.POST.get('announcement_status')
        announcement_tags = request.POST.get('announcement_tags')
        # print(program)
        # Convert the string value to a boolean
       
        announcement = Announcement.objects.get(id = id)
        announcement.title = announcement_title
        announcement.description = announcement_description
        announcement.banner = announcement_banner
        
        if announcement_status == '1':
            announcement.status = True
        elif announcement_status == '0':
            announcement.status = False
        else:
            # Handle case where no valid status is provided
            announcement.status = None  # or keep it unchanged
        # announcement.status = announcement_status,
        
        if announcement_tags:
            # Split the tags into a list
            tags_list = [tag.strip() for tag in announcement_tags.split(',')]
            # Clear existing tags and add new ones
            announcement.tags.set(*tags_list)  # Use set() to replace existing tags
        
        announcement.save()
        
        messages.success(request, "Announcement successfully updated")
        return redirect('view_announcement')
    return render(request, 'hoo/edit_announcement.html')

def MEMBERSHIP_REGISTRATION(request):
    schoolyear = School_Year.objects.all()
    
    context = {
        'schoolyear':schoolyear,
    }
    # print(teacher)
    return render(request, 'hoo/membership_registration.html', context)


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
        membership = get_object_or_404(Membership, member_id=member.id)

        if action == "approve":
            membership.status = "APPROVED"
            membership.save()

            # ✅ Generate new password
            password = get_random_string(length=10)
            user.set_password(password)

            # ✅ Activate the user
            user.is_active = 1
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
                request, f"Membership for {user.first_name} {user.last_name} approved, user activated, and email with credentials sent."
            )

        elif action == "decline":
            membership.status = "DECLINED"
            membership.save()

            messages.warning(
                request, f"Membership for {user.first_name} {user.last_name} declined."
            )
        else:
            messages.error(request, "Invalid action.")

        return redirect("membership_approval")

    # --- GET logic ---
    members = Member.objects.select_related('admin', 'organization', 'membershiptype')
    memberships = Membership.objects.only('member_id', 'status', 'proof_of_payment')

    # Map status and proof_of_payment to member_id
    membership_status_map = {m.member_id: m.status for m in memberships}
    membership_payment_map = {m.member_id: m.proof_of_payment for m in memberships}

    # Add dynamic attributes for display
    for member in members:
        member.status = membership_status_map.get(member.id, 'PENDING')
        member.proof_of_payment = membership_payment_map.get(member.id, None)

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

    return render(request, 'hoo/membership_approval.html', context)



def VIEWALL_EVENT(request):
    # Fetch all events with related school year to reduce queries
    events = Event.objects.select_related('school_year').all()
    return render(request, 'hoo/viewall_event.html', {'events': events})



def GET_EVENT_JSON(request, id):
    """Return event details as JSON for the View modal."""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            event = Event.objects.get(pk=id)
            data = {
                "id": event.id,
                "title": event.title,
                "theme": event.theme,
                "date": event.date.strftime("%Y-%m-%d") if event.date else "",
                "location": event.location,
                "max_attendees": event.max_attendees,
                "registration_fee": str(event.registration_fee) if event.registration_fee else "",
                "school_year": f"{event.school_year.sy_start} - {event.school_year.sy_end}" if event.school_year else "N/A",
            }
            return JsonResponse(data)
        except Event.DoesNotExist:
            raise Http404("Event not found")
    else:
        raise Http404("Invalid request")

def ADD_EVENT(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        theme = request.POST.get('theme')
        date = request.POST.get('date')
        location = request.POST.get('location')
        max_attendees = request.POST.get('max_attendees')
        registration_fee = request.POST.get('registration_fee')
        chair_id = request.POST.get('chair')
        co_chair_id = request.POST.get('co_chair')
        registration_link = request.POST.get('registration_link')
        evaluation_link = request.POST.get('evaluation_link')

        banner = request.FILES.get('banner')
        qr_code = request.FILES.get('qr_code')

        # ✅ Get active school year
        try:
            active_schoolyear = School_Year.objects.get(status=1)
        except School_Year.DoesNotExist:
            messages.error(request, "No active school year found. Please activate a school year first.")
            return redirect('add_event')

        # ✅ Deactivate previous active events
        Event.objects.filter(status='active').update(status='inactive')

        # ✅ Create and save new event
        event = Event(
            title=title,
            theme=theme,
            date=date,
            location=location,
            max_attendees=max_attendees,
            registration_fee=registration_fee,
            chair_id=chair_id,
            co_chair_id=co_chair_id,
            registration_link=registration_link,
            evaluation_link=evaluation_link,
            banner=banner,
            qr_code=qr_code,
            created_by=request.user,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            school_year=active_schoolyear,
            status='active',
            available_slots=max_attendees
        )
        event.save()

        messages.success(
            request,
            f'Event added successfully for cycle {active_schoolyear.sy_start.year} - {active_schoolyear.sy_end.year}!'
        )
        return redirect('viewall_event')

    # Fetch dropdown data
    members = Member.objects.all()
    officertypes = OfficerType.objects.all()
    custom_users = CustomUser.objects.filter(user_type__in=[1, 2], is_superuser=0)

    # ✅ Map officertype names to each custom user
    for user in custom_users:
        try:
            member = members.get(admin_id=user.id)
            officer_type = officertypes.get(id=member.officertype_id)
            user.officertype_name = officer_type.name
        except (Member.DoesNotExist, OfficerType.DoesNotExist):
            user.officertype_name = "N/A"

    # ✅ Active school year for template
    active_schoolyear = School_Year.objects.filter(status=1).first()

    return render(request, 'hoo/add_event.html', {
        'members': members,
        'custom_users': custom_users,
        'officertypes': officertypes,
        'active_schoolyear': active_schoolyear
    })


def DELETE_EVENT(request, id):
    event = Event.objects.get(id = id)
    event.delete()
    messages.success(request, 'event successfully deleted')
    return redirect('viewall_event')



def EDIT_EVENT(request, id):
    event = get_object_or_404(Event, id=id)

    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.theme = request.POST.get('theme')
        event.date = request.POST.get('date')
        event.location = request.POST.get('location')
        event.max_attendees = request.POST.get('max_attendees')
        event.registration_fee = request.POST.get('registration_fee')

        if 'banner' in request.FILES:
            event.banner = request.FILES['banner']
        if 'qr_code' in request.FILES:
            event.qr_code = request.FILES['qr_code']

        event.save()
        messages.success(request, f'Event "{event.title}" updated successfully!')
        return redirect('viewall_event')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'theme': event.theme,
            'date': event.date.strftime('%Y-%m-%d'),
            'location': event.location,
            'max_attendees': event.max_attendees,
            'registration_fee': event.registration_fee,
        })

    return redirect('viewall_event')

