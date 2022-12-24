import datetime
from django.db import models
from django.conf import settings
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from djangoordersystem.managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify


ORDER_STATUS_CHOICES = [
    (1, "Pending"),
    (2, "On the way"),
    (3, "Ongoing"),
    (4, "Done")
]

ORDER_PAYMENT_CHOICES = [
    (1, "Cash"),
    (2, "GCash"),
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"


class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0, validators=[MinValueValidator(0)])
    discounted_price = models.FloatField(
        default=0, validators=[MinValueValidator(0),])
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    slug = models.SlugField()

    product_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def add_to_cart(self):
        return reverse('system:add-to-cart', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Service, self).save(*args, **kwargs)


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    status = models.PositiveIntegerField(
        default=1, choices=ORDER_STATUS_CHOICES)
    order_started = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"


def receipt_no_gen() -> str:
    today = datetime.date.today()
    today_string = today.strftime('%y%m%d')
    next_invoice_number = '01'
    last_invoice = OrderService.objects.filter(
        receipt_no__startswith=today_string).order_by('receipt_no').last()
    if last_invoice:
        last_invoice_number = int(last_invoice.receipt_no[6:])
        next_invoice_number = '{0:04d}'.format(last_invoice_number + 1)
    return today_string + next_invoice_number


class BillingInfo(models.Model):
    address = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    brgy = models.CharField(max_length=50)
    zip_code = models.PositiveBigIntegerField(blank=False, default=1234)

    def __str__(self):
        return self.address


class OrderService(models.Model):
    receipt_no = models.CharField(
        max_length=8, primary_key=True,  default=receipt_no_gen)
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    billing_info = models.ForeignKey(BillingInfo, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    added_on = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment_method = models.PositiveIntegerField(
        default=1, choices=ORDER_PAYMENT_CHOICES)

    scheduled_date = models.DateTimeField(auto_now_add=True)
    gcash_number = PhoneNumberField(region='PH', null=True)
    total_price = models.FloatField(
        validators=[MinValueValidator(0)], default=0)

    def __str__(self):
        return f"{self.quantity} units of {self.service.name}"
