from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .calendar_service import create_calendar_event

@receiver(post_save, sender=Order)
def order_confirmed_trigger(sender, instance, created, **kwargs):
    """
    Triggered whenever an Order is saved.
    """
    # Only act if status is CONFIRMED
    if instance.status == 'CONFIRMED' and instance.due_date:
        # We check a custom flag to prevent duplicate events
        # (Ideally, you'd add a boolean field 'is_synced_to_calendar' to your model)
        print(f"Syncing Order #{instance.id} to Calendar...")
        create_calendar_event(instance)