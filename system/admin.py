from django.contrib import admin
from .models import Service, Order, OrderService
from django.contrib.auth.models import Group
from .models import ORDER_STATUS_CHOICES
from django_reverse_admin import ReverseModelAdmin


admin.site.unregister(Group)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    fields = ('name', 'price', 'discounted_price', 'description', 'thumbnail')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

# class OrderModelInline(admin.TabularInline):
#     model = Order
# fields = ('status',)


@admin.register(OrderService)
class OrderServiceAdmin(ReverseModelAdmin):
    inline_type = 'tabular'
    inline_reverse = [('receipt_no', 'total_price', 'user', 'service',
                       'quantity', 'confirmed', 'added_on', 'scheduled_date', 'payment_method', 'gcash_number', 'paid'),
                      ('order', {'fields': [
                       'status', ]}),
                      ]
    readonly_fields = ('receipt_no', 'total_price', 'user', 'service',
                       'scheduled_date', 'payment_method', 'quantity', 'gcash_number', 'added_on')
    list_display = ('receipt_no', 'service', 'order', 'quantity',
                    'confirmed', 'status', 'added_on', 'scheduled_date')


# @admin.register(OrderService)
# class OrderServiceAdmin(admin.ModelAdmin):
#     list_display = ('receipt_no', 'service', 'order', 'quantity',
#                     'confirmed', 'status', 'added_on', 'scheduled_date')
#     fields = ('receipt_no', 'user', 'service',
#               'quantity', 'confirmed', 'added_on', 'scheduled_date', 'payment_method', 'gcash_number', 'paid')
#     readonly_fields = ('receipt_no', 'user', 'service',
#                        'scheduled_date', 'payment_method', 'quantity', 'gcash_number', 'added_on')
#     inlines = (OrderModelInline,)
    # fieldsets = (
    #     (None, {
    #         'fields': (
    #             ('order',),
    #             ('receipt_no', 'user', 'service',
    #              'quantity', 'confirmed', 'added_on', 'scheduled_date', 'payment_method', 'gcash_number', 'paid')
    #         ),
    #     }),
    # )


    def status(self, obj):
        status_value = None
        if obj.order is not None:
            status_value = [
                tup for tup in ORDER_STATUS_CHOICES if obj.order.status in tup][0][1]
        return status_value


admin.site.site_header = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.site_title = "Green Cool Refrigeration Air-Conditioning Supply and Services Corporation"
admin.site.index_title = "Welcome to admin portal"
