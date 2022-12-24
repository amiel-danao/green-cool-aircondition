import django_tables2 as tables
from .models import OrderService


class OrderServiceTable(tables.Table):
    class Meta:
        model = OrderService
        template_name = "django_tables2/bootstrap.html"
        fields = ("receipt_no", "total_price", )
