from django.contrib import admin
from .models import Truck

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('id', 'plate_number', 'model', 'year', 'get_user_name')
    list_filter = ('year', 'model')
    search_fields = ('plate_number', 'model', 'user__first_name', 'user__last_name')
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.user.get_full_name()
        return '-'
    get_user_name.short_description = 'User'
