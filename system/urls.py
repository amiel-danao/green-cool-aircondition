from django.urls import path

from system.models import Service
from .views import OrderServiceListView, ServiceListView, ServiceDetailView, home_view, logout_view, register_view, cart_summary, add_to_cart
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, LoginForm
from django.contrib.auth import views as auth_views

app_name = 'system'

urlpatterns = [
    path('accounts/login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True), name='login'),
    path('logout/', logout_view, name='logout'),
    path('accounts/register/', register_view, name='register'),
    path('', home_view, name='home'),
    path('services/', ServiceListView.as_view(extra_context={
         'services': Service.objects.all()}), name='services'),
    path('services/<int:pk>', ServiceDetailView.as_view(), name='service-detail'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('my_cart', cart_summary, name='cart-summary'),
    path('my_order', OrderServiceListView.as_view(), name='order-summary')
]
