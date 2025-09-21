from django.contrib import admin
from .models import *
from app.models import Announcement
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class UserModel(UserAdmin):
    list_display = ['id','last_name','first_name', 'username', 'user_type']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['is_active', 'is_staff', 'user_type']

admin.site.register(CustomUser, UserModel)
admin.site.register(Salutation)
admin.site.register(Organization)
admin.site.register(School_Year)
admin.site.register(MemberType)
admin.site.register(MembershipType)
admin.site.register(Region)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title','get_tags']
    
    def get_tags(self, obj):
        return ", ".join(o for o in obj.tags.names())

admin.site.register(OfficerType)
admin.site.register(Member)

admin.site.site_header = "TracKaPSITE | Admin Login"
admin.site.site_title = "TracKaPSITE | Administrator"
admin.site.index_title = "Welcome to TracKaPSITE Admin Dashboard"