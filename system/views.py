from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login as authlogin
from django.contrib.auth import logout as authlogout
from django.contrib.auth import authenticate as auth
from django.contrib.auth.decorators import login_required as login_required
from django.utils.timezone import make_aware
from system.context_processors import SCHEDULE_DATEFORMAT
from system.filters import OrderServiceFilter
from .models import ORDER_PAYMENT_CHOICES, ORDER_STATUS_CHOICES, BillingInfo, Service, Order, OrderService
from django.db.models import Avg, Sum, Count
from django.views.generic import ListView, DetailView
from .models import Service
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm
from django.http import HttpResponseBadRequest
from django_tables2 import Table
from .tables import OrderServiceTable
from django_tables2 import SingleTableView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from datetime import datetime
from django.utils.timezone import get_current_timezone


def home_view(request):

    context = {
        'services': Service.objects.all(),
        'register_form': RegisterForm(),
        'login_form': AuthenticationForm()
    }

    return render(request, 'index.html', context)


@login_required
def logout_view(request):
    authlogout(request)

    return redirect('system:login')


def register_view(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('system:home')
        messages.error(
            request, "Unsuccessful registration. Invalid information.")
    return render(request=request, template_name="registration/register.html", context={"form": form})


@login_required
def cart_summary(request):
    unconfirmed_orders = OrderService.objects.filter(
        user=request.user, confirmed=False)

    total_price = compute_total(unconfirmed_orders)

    if request.method == "POST":
        billing_info = None
        if unconfirmed_orders.exists():

            # First get the order ID
            order_id = unconfirmed_orders[0].order.id
            print(order_id)

            scheduled_date = request.POST.get('scheduled_date')
            if not scheduled_date:
                return HttpResponseBadRequest()
            payment_method = request.POST.get('paymentMethod')
            gcash_number = request.POST.get('gcashPhoneNumber')

            # Update ProductOrders Objects
            for order_product in unconfirmed_orders:
                order_product.confirmed = True
                order_product.payment_method = payment_method
                order_product.gcash_number = gcash_number
                order_product.scheduled_date = make_aware(datetime.strptime(
                    scheduled_date, SCHEDULE_DATEFORMAT), timezone=get_current_timezone())
                order_product.total_price = total_price
                if order_product.billing_info is None:
                    if billing_info is None:
                        billing_info = BillingInfo.objects.create(
                            address=request.POST.get('address'),
                            province=request.POST.get('province'),
                            city=request.POST.get('city'),
                            brgy=request.POST.get('brgy'),
                            zip_code=request.POST.get('zip_code'),)
                    order_product.billing_info = billing_info
                order_product.save()

            # Update the Order Object
            order = Order.objects.filter(id=order_id)[0]
            order.status = 1
            order.save()

        else:
            print("No outstanding items")

        return redirect('system:order-summary')
    elif request.method == "GET":

        items = unconfirmed_orders.aggregate(Sum('quantity'))

        context = {'my_orders': unconfirmed_orders, 'total': total_price,
                   'items': items, 'miscellaneous_fee': 0}

        return render(request, 'system/cart_summary.html', context)

    return HttpResponseBadRequest()


def compute_total(unconfirmed_orders):
    total = 0
    for order in unconfirmed_orders:
        if order.service.discounted_price > 0:
            total += order.service.discounted_price * order.quantity
        else:
            total += order.service.price * order.quantity
    return total


@login_required
def add_to_cart(request, slug):
    if request.method != "POST":
        return HttpResponseBadRequest()

    # Store the product object, given a slug
    service = get_object_or_404(Service, slug=slug)

    # Create or store Order object based on conditional
    order_queryset = Order.objects.filter(
        user=request.user, status=False)

    if order_queryset.exists():
        order = order_queryset[0]
    else:
        order = Order.objects.create(user=request.user)

    # Create OrderProduct given the above objects
    order_product = OrderService.objects.create(user=request.user,
                                                service=service,
                                                order=order,
                                                quantity=request.POST.get('quantity', 1))

    return redirect('system:cart-summary')


def about(request):
    return render(request, 'partials/_about.html')


class ServiceListView(ListView):
    model = Service


class ServiceDetailView(DetailView):
    model = Service


class OrderServiceListView(LoginRequiredMixin, SingleTableView, FilterView):
    model = OrderService
    table_class = OrderServiceTable
    template_name = 'system/order_summary.html'
    filterset_class = OrderServiceFilter
