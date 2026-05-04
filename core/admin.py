from django.contrib import admin
from .models import (
    SubscriptionPlan, Customer, Subscription, Enquiry,
    Service, Testimonial, Branch, CompanyStat
)

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'daily_price', 'badge', 'is_active', 'order']
    list_editable = ['order', 'is_active']
    search_fields = ['display_name']
    list_filter = ['is_active']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'name', 'phone', 'email', 'created_at']
    search_fields = ['name', 'phone', 'email', 'customer_id']
    list_filter = ['created_at']
    readonly_fields = ['customer_id']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_id', 'customer', 'plan', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'plan', 'start_date']
    search_fields = ['subscription_id', 'customer__name', 'customer__phone']
    readonly_fields = ['subscription_id']

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ['enquiry_id', 'name', 'phone', 'service_type', 'is_processed', 'created_at']
    list_filter = ['service_type', 'is_processed', 'created_at']
    search_fields = ['name', 'phone', 'email', 'enquiry_id']
    readonly_fields = ['enquiry_id']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating', 'is_active', 'order']
    list_editable = ['order', 'is_active']
    list_filter = ['rating', 'is_active']

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_main_branch', 'order']
    list_editable = ['order']
    search_fields = ['name', 'address']

@admin.register(CompanyStat)
class CompanyStatAdmin(admin.ModelAdmin):
    list_display = ['label', 'value', 'suffix', 'order']
    list_editable = ['order']