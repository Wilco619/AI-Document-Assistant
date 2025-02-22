from django.contrib import admin
from .models import (
    CustomUser,
    AdminUser,
)



class UserModelAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',  'user_type')  # Add fields as per your model
    list_filter = ('user_type',)  # Add filters as per your model


class AdminUserInline(admin.StackedInline):
    model = AdminUser
    can_delete = False
    verbose_name_plural = 'Admin User'

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_active')

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    

