from django.contrib import admin
from .models import Truck

@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    list_display = ('id', 'plate_number', 'model', 'year', 'get_driver_name')
    list_filter = ('year', 'model')
    search_fields = ('plate_number', 'model', 'driver__user__first_name', 'driver__user__last_name')
    
    def get_driver_name(self, obj):
        if obj.driver:
            return obj.driver.user.get_full_name()
        return '-'
    get_driver_name.short_description = 'Driver'
