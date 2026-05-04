from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enquiry

@receiver(post_save, sender=Enquiry)
def enquiry_created(sender, instance, created, **kwargs):
    """Send notification when new enquiry is created"""
    if created:
        # You can add additional logic here
        # e.g., send SMS, create notification, etc.
        pass