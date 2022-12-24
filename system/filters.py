import django_filters
from system.models import OrderService


class OrderServiceFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(
        field_name='order__status', lookup_expr='iexact')

    class Meta:
        model = OrderService
        fields = ['receipt_no', 'order',
                  'scheduled_date', 'status', 'total_price']
