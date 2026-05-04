from django import forms
from .models import Enquiry, Customer, Subscription


class EnquiryForm(forms.ModelForm):
    """Contact form for enquiries"""

    class Meta:
        model = Enquiry
        fields = ['name', 'phone', 'email', 'service_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your mobile number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'service_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us what support you need',
                'rows': 4
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number should contain only digits.')
        if phone and len(phone) < 10:
            raise forms.ValidationError('Phone number must be at least 10 digits.')
        return phone


class SubscriptionForm(forms.ModelForm):
    """Form for prince_group purchase"""

    class Meta:
        model = Subscription
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'})
        }


class QuickCustomerForm(forms.ModelForm):
    """Quick customer creation for prince_group"""

    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }