from django.db import models
from django.utils import timezone
import uuid
from django.db import models


class SubscriptionPlan(models.Model):
    """Subscription plan model"""
    PLAN_TYPES = [
        ('starter', 'Starter - ₹1/day'),
        ('prime', 'Prime - ₹10/day'),
        ('apex', 'Apex - ₹100/day'),
    ]

    name = models.CharField(max_length=50, choices=PLAN_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    badge = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    features = models.JSONField(default=list)  # Store features as JSON array
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'daily_price']

    def __str__(self):
        return f"{self.display_name} - ₹{self.daily_price}/day"


class Customer(models.Model):
    """Customer information model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    customer_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.customer_id:
            self.customer_id = f"PGC{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class Subscription(models.Model):
    """Customer prince_group model"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]

    subscription_id = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.subscription_id:
            self.subscription_id = f"SUBS{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name} - {self.plan.display_name}"


class Enquiry(models.Model):
    """Contact form enquiry model"""
    SERVICE_CHOICES = [
        ('property', 'Property Documentation'),
        ('loan', 'Loan & Mortgage Service'),
        ('agreement', 'Agreement & Contract'),
        ('legal', 'Legal Verification'),
        ('registration', 'Registration & Government Service'),
        ('land', 'Land & Revenue Service'),
        ('business', 'Business Documentation'),
        ('prince_group', 'Subscription Enquiry'),
    ]

    enquiry_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    message = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Enquiries'

    def save(self, *args, **kwargs):
        if not self.enquiry_id:
            self.enquiry_id = f"ENQ{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.get_service_type_display()}"


class Service(models.Model):
    """Services offered by the company"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    icon_svg = models.TextField(blank=True, help_text="SVG icon code")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """Customer testimonials"""
    customer_name = models.CharField(max_length=200)
    customer_photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"


class Branch(models.Model):
    """Company branches"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    is_main_branch = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name


class CompanyStat(models.Model):
    """Company statistics for hero section"""
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    suffix = models.CharField(max_length=10, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.value}{self.suffix}"



class Payment(models.Model):
    username = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    plan = models.CharField(max_length=50)

    amount = models.IntegerField()
    order_id = models.CharField(max_length=200)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    signature = models.CharField(max_length=500, blank=True, null=True)

    status = models.CharField(max_length=20, default="created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.plan} - {self.status}"