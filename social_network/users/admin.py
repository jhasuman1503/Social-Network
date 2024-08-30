
from django.contrib import admin
from .models import CustomUser
from .models import FriendRequest
# Register your models here.
@admin.register(CustomUser)
class UsersModel(admin.ModelAdmin):
    list_display = ['email','first_name','last_name','is_active','is_staff','password']

@admin.register(FriendRequest)
class UsersModel(admin.ModelAdmin):
    list_display = ['from_user','to_user','created_at','accepted','rejected']