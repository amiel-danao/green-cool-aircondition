import django_tables2 as tables
from .models import OrderService


class OrderServiceTable(tables.Table):
    price = tables.Column()

    class Meta:
        orderable = False
        model = OrderService
        template_name = "django_tables2/bootstrap.html"
        fields = ("receipt_no", "service", "scheduled_date",
                  "quantity", "order__status" )
