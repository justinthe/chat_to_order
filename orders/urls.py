from django.urls import path
from . import views

urlpatterns = [
    path('webhooks/telegram/', views.telegram_webhook, name='telegram_webhook'),
]