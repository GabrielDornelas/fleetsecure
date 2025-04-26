from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'cpf', 'is_active', 'is_admin', 'is_driver')
    list_filter = ('is_active', 'is_admin', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('cpf', 'phone_number', 'date_of_birth', 'profile_picture', 'is_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {'fields': ('cpf', 'phone_number', 'date_of_birth', 'profile_picture', 'is_admin')}),
    )
    
    def is_driver(self, obj):
        return obj.is_driver()
    is_driver.boolean = True
    is_driver.short_description = 'Driver'
