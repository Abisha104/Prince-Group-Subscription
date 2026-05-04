from django.urls import path
from subscription import views

urlpatterns = [
    path('services/', views.get_services_api, name='api_services'),
    path('testimonials/', views.get_testimonials_api, name='api_testimonials'),
    path('branches/', views.get_branches_api, name='api_branches'),
    path('plans/', views.get_plans_api, name='api_plans'),
]