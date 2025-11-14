from django.shortcuts import render,redirect, HttpResponse
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from app.models import CustomUser, Member, Membership
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

