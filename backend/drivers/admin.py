from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_full_name', 'license_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
