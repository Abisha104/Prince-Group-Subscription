import logging
from datetime import timedelta

from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from django.views.decorators.http import require_http_methods

from core.models import (
    SubscriptionPlan, Customer, Subscription, Enquiry,
    Service, Testimonial, Branch, CompanyStat
)
from core.forms import EnquiryForm, SubscriptionForm, QuickCustomerForm

logger = logging.getLogger(__name__)



import razorpay
import json
import hmac
import hashlib

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



# ---------- Main page ----------
def index(request):
    """Serves the main landing page (all dynamic data is fetched via APIs)"""
    return render(request, 'core/index.html')


# ---------- Service pages (1..10) – simple static templates ----------
# We'll use Django's TemplateView – no extra code needed.
# Just add one line per service in urls.py (see below).
# Or you can keep them as static files if you prefer, but these views ensure template loading.


# ---------- API endpoints (used by your frontend JavaScript) ----------
@require_http_methods(['GET'])
def get_services_api(request):
    services = Service.objects.filter(is_active=True).values(
        'id', 'name', 'slug', 'short_description', 'icon_svg'
    )
    return JsonResponse({'services': list(services)})


@require_http_methods(['GET'])
def get_testimonials_api(request):
    testimonials = Testimonial.objects.filter(is_active=True).values(
        'id', 'customer_name', 'rating', 'review_text'
    )
    return JsonResponse({'testimonials': list(testimonials)})


@require_http_methods(['GET'])
def get_branches_api(request):
    branches = Branch.objects.all().values(
        'id', 'name', 'address', 'phone', 'email', 'latitude', 'longitude'
    )
    return JsonResponse({'branches': list(branches)})


@require_http_methods(['GET'])
def get_plans_api(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).values(
        'id', 'display_name', 'daily_price', 'badge', 'description', 'features'
    )
    # Convert features from JSON string to list if needed
    for plan in plans:
        if isinstance(plan['features'], str):
            plan['features'] = json.loads(plan['features'])
    return JsonResponse({'plans': list(plans)})


@require_http_methods(['GET'])
def get_stats_api(request):
    stats = CompanyStat.objects.all().values('label', 'value', 'suffix')
    return JsonResponse({'stats': list(stats)})


# ---------- Contact form with auto-reply ----------
@require_http_methods(['POST'])
def submit_enquiry(request):
    form = EnquiryForm(request.POST)
    if form.is_valid():
        enquiry = form.save()

        # 1. Notify admin
        try:
            send_mail(
                subject=f'New Enquiry: {enquiry.enquiry_id}',
                message=f"""
                New enquiry received:

                Name: {enquiry.name}
                Phone: {enquiry.phone}
                Email: {enquiry.email}
                Service: {enquiry.get_service_type_display()}
                Message: {enquiry.message}

                Enquiry ID: {enquiry.enquiry_id}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Admin email failed: {e}")

        # 2. Send auto-reply to customer (if email provided)
        if enquiry.email:
            try:
                send_mail(
                    subject='Thank you for contacting Prince Group',
                    message=f"""
                    Dear {enquiry.name},

                    We have received your enquiry regarding "{enquiry.get_service_type_display()}".
                    Our team will get back to you within 24 hours.

                    Enquiry ID: {enquiry.enquiry_id}

                    Thank you for choosing Prince Group – your trusted documentation partner.

                    © Prince Group of Company
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[enquiry.email],
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f"Auto-reply to {enquiry.email} failed: {e}")

        return JsonResponse({
            'success': True,
            'message': 'Your enquiry has been submitted successfully. A confirmation email has been sent.',
            'enquiry_id': enquiry.enquiry_id
        })
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


# ---------- Subscription purchase ----------
@require_http_methods(['GET', 'POST'])
def subscription_page(request):
    # GET – display form, optionally pre‑select a plan
    plan_name = request.GET.get('plan')
    amount = request.GET.get('amount')
    selected_plan = None
    if plan_name:
        selected_plan = SubscriptionPlan.objects.filter(
            display_name__icontains=plan_name
        ).first()
        if not selected_plan and amount:
            selected_plan = SubscriptionPlan.objects.filter(daily_price=amount).first()

    if request.method == 'POST':
        customer_form = QuickCustomerForm(request.POST)
        subscription_form = SubscriptionForm(request.POST)

        if customer_form.is_valid() and subscription_form.is_valid():
            phone = customer_form.cleaned_data['phone']
            customer = Customer.objects.filter(phone=phone).first()
            if not customer:
                customer = customer_form.save()

            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)

            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=30)
            subscription = Subscription.objects.create(
                customer=customer,
                plan=plan,
                start_date=start_date,
                end_date=end_date,
                total_amount=plan.daily_price * 30,
                payment_method=subscription_form.cleaned_data['payment_method'],
                status='active'
            )
            request.session['subscription_id'] = subscription.subscription_id

            # Send confirmation email
            if customer.email:
                try:
                    send_mail(
                        subject='Subscription Confirmation – Prince Group',
                        message=f"""
                        Dear {customer.name},

                        Your {plan.display_name} subscription (₹{plan.daily_price}/day) is now active.
                        Start Date: {start_date}
                        End Date: {end_date}

                        Subscription ID: {subscription.subscription_id}

                        You can login to your dashboard using your phone number: {customer.phone}

                        Thank you for choosing Prince Group!
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[customer.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    logger.error(f"Subscription email failed: {e}")

            return JsonResponse({
                'success': True,
                'subscription_id': subscription.subscription_id,
                'redirect_url': '/subscription-success/'
            })
        else:
            errors = {**customer_form.errors, **subscription_form.errors}
            return JsonResponse({'success': False, 'errors': errors}, status=400)

    # GET request – show form
    customer_form = QuickCustomerForm()
    subscription_form = SubscriptionForm()
    context = {
        'selected_plan': selected_plan,
        'amount': amount,
        'customer_form': customer_form,
        'subscription_form': subscription_form,
        'plans': SubscriptionPlan.objects.filter(is_active=True),
    }
    return render(request, 'core/subscription.html', context)
def payment_page(request):
    """Display payment page for selected plan (reuses subscription page layout)"""
    plan_name = request.GET.get('plan')
    amount = request.GET.get('amount')
    context = {
        'plan_name': plan_name,
        'amount': amount,
        # You can also pass the plan object if needed
    }
    return render(request, 'core/payment.html', context)




# 🔹 CREATE ORDER
@csrf_exempt
def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)

        amount = int(data.get("amount")) * 100  # paise

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return JsonResponse({
            "order_id": order["id"],
            "key": settings.RAZORPAY_KEY_ID
        })


# 🔹 VERIFY PAYMENT
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        payment_id = data.get("razorpay_payment_id")
        order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature")

        generated_signature = hmac.new(
            bytes(settings.RAZORPAY_KEY_SECRET, 'utf-8'),
            bytes(order_id + "|" + payment_id, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == signature:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "failed"})



def payment_success(request):
    """Payment success page – reuse subscription success logic"""
    subscription_id = request.session.get('subscription_id')
    subscription = None
    if subscription_id:
        try:
            subscription = Subscription.objects.select_related('customer', 'plan').get(
                subscription_id=subscription_id
            )
        except Subscription.DoesNotExist:
            pass
    return render(request, 'core/payment-success.html', {'subscription': subscription})

# ---------- Customer Login & Dashboard ----------
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            customer = Customer.objects.get(phone=phone)
            request.session['customer_id'] = customer.customer_id
            request.session['customer_name'] = customer.name
            messages.success(request, f'Welcome back, {customer.name}!')
            return redirect('customer_dashboard')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found with this phone number.')
    return render(request, 'core/login.html')


def customer_dashboard(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')   # ✅ FIXED

    try:
        customer = Customer.objects.get(customer_id=customer_id)

        subscriptions = Subscription.objects.filter(customer=customer).select_related('plan')
        enquiries = Enquiry.objects.filter(phone=customer.phone)

        context = {
            'customer': customer,
            'subscriptions': subscriptions,
            'enquiries': enquiries,
            'active_subscription': subscriptions.filter(status='active').first(),
        }

        return render(request, 'core/dashboard.html', context)

    except Customer.DoesNotExist:
        request.session.flush()
        return redirect('login')




def logout_view(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')



