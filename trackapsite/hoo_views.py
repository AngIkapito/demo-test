from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.urls import path, include, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import CustomUser, Event, School_Year,Announcement, Salutation,Organization, MemberType, MembershipType, Member, OfficerType, Region
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import JsonResponse
import datetime

# Create your views here.
@login_required(login_url='/')
def home(request):
    members = Member.objects.all()
    events = Event.objects.all()
    
    context = {
        'members': members,
        'events': events,
    }
    
    return render(request,'hoo/home.html', context)

# For Schoolyear 
def ADD_SCHOOLYEAR(request):
    if request.method == "POST":
        sy_start = request.POST.get('sy_start')
        sy_end = request.POST.get('sy_end')
        # print(program_name)
        school_year = School_Year (
            sy_start = sy_start,
            sy_end = sy_end,
            created_by_id=request.user.id  # Set the created_by_username to the current user
        )
        school_year.save()
        messages.success(request, 'Cycle successfully added!')
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

def VIEWALL_EVENT(request):
    event = Event.objects.all()
    
    context = {
        'event':event,
    }
    # print(teacher)
    return render(request, 'hoo/viewall_event.html', context)

