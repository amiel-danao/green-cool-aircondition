from django.contrib import admin

from system.context_processors import SCHEDULE_DATEFORMAT_24H
from .models import Service, Order, OrderService
from django.contrib.auth.models import Group
from .models import ORDER_STATUS_CHOICES
from django_reverse_admin import ReverseModelAdmin
from django.utils.timezone import make_aware
from datetime import datetime
from django.utils.timezone import get_current_timezone

admin.site.unregister(Group)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fields = ('name', 'price', 'discounted_price', 'description', 'thumbnail')


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
        status_value = None
        if obj.order is not None:
            status_value = [
                tup for tup in ORDER_STATUS_CHOICES if obj.order.status in tup][0][1]
        return status_value


admin.site.site_header = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.site_title = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.index_title = "Welcome to admin portal"
