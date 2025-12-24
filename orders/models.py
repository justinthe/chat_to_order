from django.db import models
from django.utils import timezone

class Customer(models.Model):
    PLATFORM_CHOICES = [
        ('WA', 'WhatsApp'),
        ('TG', 'Telegram'),
    ]
    
    # Unique ID from the platform (Phone number or User ID)
    chat_id = models.CharField(max_length=50, unique=True, db_index=True)
    platform = models.CharField(max_length=2, choices=PLATFORM_CHOICES)
    
    # We allow these to be blank initially; the LLM might extract the name later
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name or 'Unknown'} ({self.chat_id})"

class RawMessage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='messages')
    
    # The actual text content
    text = models.TextField()
    
    # Store the full webhook payload (useful for debugging)
    meta_data = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Status flags for the AI
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Msg from {self.customer} @ {self.timestamp:%H:%M}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Confirmation'),
        ('CONFIRMED', 'Confirmed'), 
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    source_message = models.ForeignKey(RawMessage, on_delete=models.SET_NULL, null=True, blank=True)
    
    client_name = models.CharField(max_length=100, blank=True, null=True, help_text="The actual person buying the food")
    
    # Data extracted by LLM
    item_description = models.TextField()

    calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    
    quantity = models.PositiveIntegerField(default=1)
    
    # --- NEW FIELD ---
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        null=True, 
        blank=True, 
        help_text="Price in IDR (e.g., 50000)"
    )
    # -----------------

    due_date = models.DateTimeField(null=True, blank=True)
    
    # AI Metadata
    ai_confidence = models.FloatField(default=1.0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # I updated this to show price in the string representation too
        price_display = f"Rp {self.price:,}" if self.price else "Rp ?"
        return f"{self.client_name} : {self.quantity}x {self.item_description} - {price_display} ({self.status})"