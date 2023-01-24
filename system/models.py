import datetime
from django.db import models
from django.conf import settings
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from djangoordersystem.managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify




class PaymentMethod(models.IntegerChoices):
    CASH = 1, "Cash"
    GCASH = 2, "GCash"

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_technician = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=False)
    first_name = models.CharField(max_length=30, default='', blank=False)
    middle_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='', blank=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class TechnicianProfile(UserProfile):
    pass

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

class Status(models.IntegerChoices):
    PENDING = 1, "Pending"
    ON_THE_WAY = 2, "On the way"
    ONGOING = 3, "Ongoing"
    DONE = 4, "Done"

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    status = models.PositiveIntegerField(
        default=Status.PENDING, choices=Status.choices)
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
        next_invoice_number = '{0:02d}'.format(last_invoice_number + 1)
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
        default=PaymentMethod.CASH, choices=PaymentMethod.choices)

    scheduled_date = models.DateTimeField(auto_now_add=True)
    gcash_number = PhoneNumberField(region='PH', null=True)
    total_price = models.FloatField(
        validators=[MinValueValidator(0)], default=0)

    @property
    def price(self):
        if self.service.price:
            return self.service.price * self.quantity
        elif self.service.discounted_price:
            return self.service.discounted_price * self.quantity
        return 0

    def __str__(self):
        return self.receipt_no


class Task(models.Model):
    order = models.OneToOneField(OrderService, on_delete=models.CASCADE)
    technician = models.ForeignKey(TechnicianProfile, on_delete=models.CASCADE)
    date_assigned = models.DateTimeField(auto_now_add=True)
    date_finished = models.DateTimeField(null=True)
    
    class Meta:
        unique_together = ('order', 'technician')

    def __str__(self):
        return f'{self.order.receipt_no}-{self.technician}'

    def save(self, *args, **kwargs):
        if self.order.order.status == Status.DONE:
            self.date_finished = timezone.now()
        else:
            self.date_finished = None
        return super().save(*args, **kwargs)


class ServiceFeedback(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    feedback = models.CharField(max_length=256, blank=False, default='')
    rating = models.IntegerField(default=0, validators=(MinValueValidator(0), MaxValueValidator(5)))
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.task.order.receipt_no}-{self.task.technician}'