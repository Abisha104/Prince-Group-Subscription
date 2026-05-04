from django.urls import path
from django.views.generic import TemplateView
from . import views
from django.urls import path
from .views import create_order, verify_payment


app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('subscription.html', views.subscription_page, name='subscription_html'),
    path('payment.html', views.payment_page, name='payment_html'),
    path('payment-success.html', views.payment_success, name='payment_success_html'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('logout/', views.logout_view, name='logout'),


path('branch.html', TemplateView.as_view(template_name='core/branch.html'), name='branch'),
path('customer.html', TemplateView.as_view(template_name='core/customer.html'), name='customer'),
path('fastresponse.html', TemplateView.as_view(template_name='core/fastresponse.html'), name='fastresponse'),
    # Form submission (AJAX)
    path('submit-enquiry/', views.submit_enquiry, name='submit_enquiry'),

    # API endpoints (used by your frontend JavaScript)
    path('api/services/', views.get_services_api, name='api_services'),
    path('api/testimonials/', views.get_testimonials_api, name='api_testimonials'),
    path('api/branches/', views.get_branches_api, name='api_branches'),
    path('api/plans/', views.get_plans_api, name='api_plans'),
    path('api/stats/', views.get_stats_api, name='api_stats'),

    # Service pages (1 to 10) – simply render the existing templates
    path('service1.html', TemplateView.as_view(template_name='core/service1.html'), name='service1'),
    path('service2.html', TemplateView.as_view(template_name='core/service2.html'), name='service2'),
    path('service3.html', TemplateView.as_view(template_name='core/service3.html'), name='service3'),
    path('service4.html', TemplateView.as_view(template_name='core/service4.html'), name='service4'),
    path('service5.html', TemplateView.as_view(template_name='core/service5.html'), name='service5'),
    path('service6.html', TemplateView.as_view(template_name='core/service6.html'), name='service6'),
    path('service7.html', TemplateView.as_view(template_name='core/service7.html'), name='service7'),
    path('service8.html', TemplateView.as_view(template_name='core/service8.html'), name='service8'),
    path('service9.html', TemplateView.as_view(template_name='core/service9.html'), name='service9'),
    path('service10.html', TemplateView.as_view(template_name='core/service10.html'), name='service10'),


path('create-order/', create_order),
    path('verify-payment/', verify_payment),
]

