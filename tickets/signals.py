# tickets/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Order

@receiver(post_delete, sender=Order)
def restore_ticket_quantity(sender, instance, **kwargs):
    if instance.status in ['cancelled']:
        ticket = instance.ticket
        ticket.sold = max(0, ticket.sold - instance.quantity)
        ticket.save()
