from django.contrib import admin
from .models import Customer, RawMessage, Order

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'name', 'platform')
    search_fields = ('name', 'chat_id')

@admin.register(RawMessage)
class RawMessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'timestamp', 'is_processed')
    list_filter = ('is_processed', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Added 'price' to this list
    list_display = ('customer', 'item_description', 'price', 'due_date', 'status', 'ai_confidence')
    list_filter = ('status', 'due_date')
    search_fields = ('item_description',)