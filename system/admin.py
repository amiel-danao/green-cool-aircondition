from django.contrib import admin

from system.context_processors import SCHEDULE_DATEFORMAT_24H
from .models import CustomUser, Service, Order, OrderService, ServiceFeedback, Status, Task, TechnicianProfile
from django.contrib.auth.models import Group
from django_reverse_admin import ReverseModelAdmin
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils.timezone import get_current_timezone

admin.site.unregister(Group)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fields = ('name', 'price', 'discounted_price', 'description', 'thumbnail')
    list_display = ('name', 'price', 'discounted_price', )

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    fields = ('email', 'picture', 'is_active', 'is_superuser', 'is_technician', 'last_login')
    readonly_fields = ('email', 'last_login')
    list_display = ('email', 'is_active', 'is_superuser', 'is_technician', 'last_login')


@admin.register(OrderService)
class OrderServiceAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    fields = ('confirmed', 'paid', 'receipt_no', 'total_price', 'user', 'service_name',
              'quantity', 'added_on', 'scheduled_date', 'payment_method', 'gcash_number')
    inline_reverse = [
        ('order', {'fields': [
            'status', ]}),
        ('billing_info', {'fields': [
                          'address', 'province', 'city', 'brgy', 'zip_code']}),
    ]
    readonly_fields = ('receipt_no', 'total_price', 'user', 'service_name',
                       'scheduled_date', 'payment_method', 'quantity', 'gcash_number', 'added_on')
    list_display = ('receipt_no', 'service', 'order', 'quantity',
                    'confirmed', 'status', 'added_on', 'scheduled_date')

    # def schedule_date(self, obj):
    #     return obj.scheduled_date.strftime('%b %d, %Y, %H:%M %p')

    def service_name(self, obj):
        return obj.service.name

    def status(self, obj):
        return Status(obj.order.status).label

@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(admin.ModelAdmin):
    pass



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('technician', 'order_status', 'date_finished')
    readonly_fields = ('date_finished',)

    def order_status(self, obj):
        return Status(obj.order.order.status).label

@admin.register(ServiceFeedback)
class ServiceFeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'feedback', 'rating')
    readonly_fields = ('task', 'feedback', 'rating')

admin.site.site_header = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.site_title = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.index_title = "Welcome to admin portal"
