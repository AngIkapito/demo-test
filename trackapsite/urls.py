from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .import views, hoo_views, member_views, officer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HOMEPAGE, name='homepage'),
    path('about/', views.ABOUT, name='about'),
    path('contact/', views.CONTACT, name='contact'),
    path('announcement/', views.ANNOUNCEMENT, name='announcement'),
    path('event/', views.EVENT, name='event'),
    path('base/',views.BASE,name='base'),
    path('registration/', views.REGISTRATION, name='registration'),
    path('registration_new/', views.REGISTRATION_NEW, name='registration_new'),
    path('registration_renew/', views.REGISTRATION_RENEW, name='registration_renew'),
    path('error/', views.ERRORPAGE, name='error_page'),  # Define the error page URL
    # path('forgot_password/', views.FORGOT_PASSWORD, name='forgot_password'),

    #Login
    path('login', views.LOGIN,name='login'),
    path('doLogin', views.doLogin, name='doLogin'),
    path('doLogout', views.doLogout, name='logout'),
    
    # Profile Update
    path('profile', views.PROFILE, name='profile'),
    path('profile/update',views.PROFILE_UPDATE, name='profile_update'),
    
    #President/Admin/Head of Organization Panel
    path('hoo/home', hoo_views.home, name='hoo_home'),
    # path('hoo/member_detail', hoo_views.MEMBER_DETAIL, name='member_detail'),
    
    #add Member
    path('hoo/Member/Add', hoo_views.ADD_MEMBER, name='add_member'),
    path('hoo/Member/ViewAll', hoo_views.VIEWALL_MEMBER, name='viewall_member'),
    path('hoo/Member/Edit/<str:id>', hoo_views.EDIT_MEMBER, name='edit_member'),
    path('hoo/Member/Update', hoo_views.UPDATE_MEMBER, name='update_member'),
    path('hoo/Member/Delete/<str:id>', hoo_views.DELETE_MEMBER, name='delete_member'),
    path('hoo/Member/View/MemberDetails/<str:id>', hoo_views.MEMBER_DETAILS, name='member_details'),
    
    #Add Schoolyear/Cycle
    path('hoo/SchoolYear/Add', hoo_views.ADD_SCHOOLYEAR, name='add_schoolyear'),
    path('hoo/SchoolYear/View', hoo_views.VIEW_SCHOOLYEAR, name='view_schoolyear'),
    path('hoo/SchoolYear/Edit/<str:id>', hoo_views.EDIT_SCHOOLYEAR, name='edit_schoolyear'),
    path('hoo/SchoolYear/Update', hoo_views.UPDATE_SCHOOLYEAR, name='update_schoolyear'),
    path('hoo/SchoolYear/Delete/<str:id>', hoo_views.DELETE_SCHOOLYEAR, name='delete_schoolyear'),
    
    #Add Regions / Chapters
    path('hoo/Region/Add', hoo_views.ADD_REGION, name='add_region'),
    path('hoo/Region/View', hoo_views.VIEW_REGION, name='view_region'),
    path('hoo/Region/Edit/<str:id>', hoo_views.EDIT_REGION, name='edit_region'),
    path('hoo/Region/Update', hoo_views.UPDATE_REGION, name='update_region'),
    path('hoo/Region/Delete/<str:id>', hoo_views.DELETE_REGION, name='delete_region'),
    
    #Add OfficerType
    path('hoo/OfficerType/Add', hoo_views.ADD_OFFICERTYPE, name='add_officertype'),
    path('hoo/OfficerType/View', hoo_views.VIEW_OFFICERTYPE, name='view_officertype'),
    path('hoo/OfficerType/Edit/<str:id>', hoo_views.EDIT_OFFICERTYPE, name='edit_officertype'),
    path('hoo/OfficerType/Update', hoo_views.UPDATE_OFFICERTYPE, name='update_officertype'),
    path('hoo/OfficerType/Delete/<str:id>', hoo_views.DELETE_OFFICERTYPE, name='delete_officertype'),
    
    #Add MembershipType
    path('hoo/MembershipType/Add', hoo_views.ADD_MEMBERSHIPTYPE, name='add_membershiptype'),
    path('hoo/MembershipType/View', hoo_views.VIEW_MEMBERSHIPTYPE, name='view_membershiptype'),
    path('hoo/MembershipType/Edit/<str:id>', hoo_views.EDIT_MEMBERSHIPTYPE, name='edit_membershiptype'),
    path('hoo/MembershipType/Update', hoo_views.UPDATE_MEMBERSHIPTYPE, name='update_membershiptype'),
    path('hoo/MembershipType/Delete/<str:id>', hoo_views.DELETE_MEMBERSHIPTYPE, name='delete_membershiptype'),
    
    #Add MemberType
    path('hoo/MemberType/Add', hoo_views.ADD_MEMBERTYPE, name='add_membertype'),
    path('hoo/MemberType/View', hoo_views.VIEW_MEMBERTYPE, name='view_membertype'),
    path('hoo/MemberType/Edit/<str:id>', hoo_views.EDIT_MEMBERTYPE, name='edit_membertype'),
    path('hoo/MemberType/Update', hoo_views.UPDATE_MEMBERTYPE, name='update_membertype'),
    path('hoo/MemberType/Delete/<str:id>', hoo_views.DELETE_MEMBERTYPE, name='delete_membertype'),
    
    #Add Organization
    path('hoo/Organization/Add', hoo_views.ADD_ORGANIZATION, name='add_organization'),
    path('hoo/Organization/View', hoo_views.VIEW_ORGANIZATION, name='view_organization'),
    path('hoo/Organization/Edit/<str:id>', hoo_views.EDIT_ORGANIZATION, name='edit_organization'),
    path('hoo/Organization/Update', hoo_views.UPDATE_ORGANIZATION, name='update_organization'),
    path('hoo/Organization/Delete/<str:id>', hoo_views.DELETE_ORGANIZATION, name='delete_organization'),
    
     #Add Static Announcement
    path('hoo/Announcement/Add', hoo_views.ADD_ANNOUNCEMENT, name='add_announcement'),
    path('hoo/Announcement/View', hoo_views.VIEW_ANNOUNCEMENT, name='view_announcement'),
    path('hoo/Announcement/Edit/<str:id>', hoo_views.EDIT_ANNOUNCEMENT, name='edit_announcement'),
    path('hoo/Announcement/Update', hoo_views.UPDATE_ANNOUNCEMENT, name='update_announcement'),
    path('hoo/Announcement/Delete/<str:id>', hoo_views.DELETE_ANNOUNCEMENT, name='delete_announcement'),
    
    #Add Salutation
    # path('hoo/Salutation/Add', hoo_views.ADD_SALUTATION, name='add_salutation'),
    # path('hoo/Salutation/View', hoo_views.VIEW_SALUTATION, name='view_salutation'),
    # path('hoo/Salutation/Edit/<str:id>', hoo_views.EDIT_SALUTATION, name='edit_salutation'),
    # path('hoo/Salutation/Update', hoo_views.UPDATE_SALUTATION, name='update_salutation'),
    # path('hoo/Salutation/Delete/<str:id>', hoo_views.DELETE_SALUTATION, name='delete_salutation'),
    
    #Event List
    path('hoo/Event/ViewAll', hoo_views.VIEWALL_EVENT, name='viewall_event'),
    #July 15 2025 11:41pm
    #path('hoo/Event/Add', hoo_views.ADD_EVENT, name='add_event'),
    #path('hoo/Event/Edit/<str:id>', hoo_views.EDIT_EVENT, name='edit_event'),
    #path('hoo/Event/Delete/<str:id>', hoo_views.DELETE_EVENT, name='delete_event'),
    #path('hoo/Event/Update', hoo_views.UPDATE_EVENT, name='update_event'),
    
    path('hoo/MembershipRegistration/View', hoo_views.MEMBERSHIP_REGISTRATION, name='membership_registration'),
    
    #Officer Panel
    path('officer/home', officer_views.home, name='officer_home'),
    
    #Member Panel
    path('member/home', member_views.home, name='member_home'),
    path('member/basic_information', member_views.basic_information, name='basic_information'),
    #path('member/registration_member', member_views.REGISTRATION_MEMBER, name='registration_member'),
    
]+ static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)