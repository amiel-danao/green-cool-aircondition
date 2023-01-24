from django.urls import path

from system.models import Service
from django.contrib.auth.forms import AuthenticationForm
from system.views import CustomLoginView, MyTaskListView, OrderServiceDetailView, OrderServiceListView, ServiceListView, ServiceDetailView, TaskDetailView, UserProfileUpdateView, home_view, logout_view, register_view, cart_summary, add_to_cart, about, delete_order, submit_feedback, task_status_update
from system.forms import RegisterForm, LoginForm
from django.contrib.auth import views as auth_views
from django.views.generic.edit import DeleteView
from django.urls import re_path

app_name = 'system'

urlpatterns = [
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/register/', register_view, name='register'),
    path('', home_view, name='home'),
    path('services/', ServiceListView.as_view(extra_context={
         'services': Service.objects.all()}), name='services'),
    path('services/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('order_delete/<int:pk>/', delete_order, name='order-delete'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('my_cart', cart_summary, name='cart-summary'),
    path('about/', about, name='about'),
    path('my_order', OrderServiceListView.as_view(), name='order-summary'),
    path('order_detail/<pk>', OrderServiceDetailView.as_view(), name='order-detail'),
    path('profile_detail/<pk>', UserProfileUpdateView.as_view(), name='profile-detail'),
    path('my_tasks/', MyTaskListView.as_view(), name='my_tasks'),
    path('task_detail/<pk>', TaskDetailView.as_view(), name='task-detail'),
    path('task_status_update/<pk>/<int:status>', task_status_update, name='task-status-update'),    
    path('submit_feedback/<pk>', submit_feedback, name='submit_feedback')
]
