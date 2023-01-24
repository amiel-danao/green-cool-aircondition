from django.contrib import messages
from django.contrib.auth.signals import user_logged_in
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login as authlogin
from django.contrib.auth import logout as authlogout
from django.contrib.auth import authenticate as auth
from django.contrib.auth.decorators import login_required as login_required
from django.utils.timezone import make_aware
from system.context_processors import SCHEDULE_DATEFORMAT
from system.filters import OrderServiceFilter
from .models import BillingInfo, Service, Order, OrderService, ServiceFeedback, Status, Task, TechnicianProfile, UserProfile
from django.db.models import Avg, Sum, Count
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from .models import Service
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import LoginForm, OrderServiceForm, RegisterForm, ServiceFeedbackForm, UserProfileForm
from django.http import HttpResponseBadRequest
from django_tables2 import Table
from .tables import OrderServiceTable, TaskTable
from django_tables2 import SingleTableView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from datetime import datetime
from django.utils import timezone
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
            technician = request.POST.get('is_technician', False)
            user.is_technician = True if technician == 'on' else False
            if user.is_technician:
                user.is_active = False
            user.save()
            if user.is_technician:
                TechnicianProfile.objects.create(user=user, 
                first_name=request.POST.get('first_name', ''),
                middle_name=request.POST.get('middle_name', ''),
                last_name=request.POST.get('last_name', ''))
            else:
                UserProfile.objects.create(user=user, 
                first_name=request.POST.get('first_name', ''),
                middle_name=request.POST.get('middle_name', ''),
                last_name=request.POST.get('last_name', ''))
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
                order_product.order.status = 1
                order_product.order.save()


            # Update the Order Object
            # order = Order.objects.filter(id=order_id)[0]
            # order.status = 1
            # order.save()

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
    # order_queryset = Order.objects.filter(
    #     user=request.user, status=False)

    # if order_queryset.exists():
    #     order = order_queryset[0]
    # else:
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


class OrderServiceListView(LoginRequiredMixin, SingleTableView):
    model = OrderService
    table_class = OrderServiceTable
    template_name = 'system/order_summary.html'
    # filterset_class = OrderServiceFilter
    per_page = 8

    def get_table_data(self):
        return OrderService.objects.filter(user=self.request.user, confirmed=True)

class OrderServiceDetailView(LoginRequiredMixin, DetailView):
    model = OrderService
    template_name = 'system/order_details.html'

    def get_context_data(self, **kwargs):
        context = super(OrderServiceDetailView, self).get_context_data(**kwargs)
        
        context['service'] = self.object.service
        context['status'] = Status(self.object.order.status).label
        context['form'] = OrderServiceForm()
        technician = 'Not yet assigned'
        task = Task.objects.filter(order=self.object).first()
        if task and task.technician is not None:
            technician = task.technician
        context['technician'] = technician

        task = Task.objects.filter(order=self.object).first()
        feedback = ServiceFeedback.objects.filter(task=task).first()
        context['has_feedback'] = feedback
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    template_name = 'system/profile_details.html'
    fields = [
        "first_name",
        "middle_name",
        "last_name",
    ]
    
    def get_success_url(self):
        return reverse('system:profile-detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super(UserProfileUpdateView, self).get_form(form_class)
        form.fields['middle_name'].required = False
        return form

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdateView, self).get_context_data(**kwargs)
        
        context['form'] = UserProfileForm(initial=self.object.__dict__)
            
        return context

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super().form_invalid(form)


def delete_order(request, pk):
    order_service = get_object_or_404(OrderService, pk=pk)
    order = get_object_or_404(Order, pk=order_service.order.pk)
    order.delete()
    order_service.delete()
    return redirect('system:cart-summary')

class TechnicianOnlyView(object):

    def has_permissions(self):
        if self.request.user.is_technician:
            return True
        return False

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise Http404('You do not have permission.')
        return super(TechnicianOnlyView, self).dispatch(
            request, *args, **kwargs)

class TaskDetailView(LoginRequiredMixin, TechnicianOnlyView, DetailView):
    model = Task
    template_name = 'system/task_details.html'

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        
        customer_profile = UserProfile.objects.filter(user=self.object.order.user).first()
        if customer_profile:
            context['customer_name'] = f'{customer_profile.first_name} {customer_profile.last_name}'
        else:
            context['customer_name'] = self.object.order.user.email
        context['service'] = self.object.order.service
        context['status'] = Status(self.object.order.order.status).label
        if self.object.order.order.status != Status.DONE:
            context['next_status'] = Status(self.object.order.order.status+1).label
        return context

class MyTaskListView(LoginRequiredMixin, TechnicianOnlyView, SingleTableView):
    model = Task
    table_class = TaskTable
    template_name = 'system/my_tasks.html'
    # filterset_class = OrderServiceFilter
    per_page = 8

    def get_table_data(self):
        technician_profile = TechnicianProfile.objects.filter(user=self.request.user).first()
        if technician_profile is None:
            return Task.objects.none()
        return Task.objects.filter(technician=technician_profile)



class CustomLoginView(LoginView):
    authentication_form=LoginForm
    redirect_authenticated_user=True

def login_handler(sender, user, request, **kwargs):
    existing_profile = UserProfile.objects.filter(user=user).first()
    if existing_profile is None:
        local, at, domain = user.email.rpartition('@')
        if user.is_technician:
            TechnicianProfile.objects.create(user=user, 
            first_name=local,
            last_name=local)
        else:
            UserProfile.objects.create(user=user, 
            first_name=local,
            last_name=local)
        print(local)
    

user_logged_in.connect(login_handler)

@login_required
def task_status_update(request, pk, status):
    if not request.user.is_technician:
        return HttpResponseForbidden()
    task = get_object_or_404(Task, pk=pk)
    task.order.order.status = status
    task.order.order.save()
    task.save()

    return redirect('system:task-detail', pk=pk)


@login_required
def submit_feedback(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    order = get_object_or_404(OrderService, pk=pk)

    task = get_object_or_404(Task, order=order)
    ServiceFeedback.objects.create(task=task, feedback=request.POST.get('feedback', ''), rating=request.POST.get('rating', 0))

    return redirect('system:order-detail', pk=order.pk)
