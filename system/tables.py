from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import django_tables2 as tables
from .models import OrderService, Task


class OrderServiceTable(tables.Table):
    total_price = tables.Column()

    class Meta:
        orderable = True
        model = OrderService
        template_name = "django_tables2/bootstrap.html"
        fields = ("receipt_no", "service", "scheduled_date",
                  "quantity", "order__status" )
        attrs = {'class': 'table table-hover shadow records-table'}
        row_attrs = {
            "onClick": lambda record: f"document.location.href='{reverse('system:order-detail', kwargs={'pk': record.pk})}';"
        }
        


class TaskTable(tables.Table):
    

    class Meta:
        orderable = True
        model = Task
        template_name = "django_tables2/bootstrap.html"
        fields = ("order__receipt_no", "order__order__status", "date_assigned", "date_finished")
        attrs = {'class': 'table table-hover shadow records-table'}
        empty_text = _("No tasks")
        row_attrs = {
            "onClick": lambda record: f"document.location.href='{reverse('system:task-detail', kwargs={'pk': record.pk})}';"
        }