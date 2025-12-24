import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Customer, RawMessage, Order
from .ai_service import parse_order_with_ai
from .telegram_utils import send_telegram_reply 
from .calendar_service import create_calendar_event, delete_calendar_event 
from django.utils import timezone
from datetime import timedelta


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Safety Check 1: Does 'message' exist?
            if 'message' not in data:
                return JsonResponse({'status': 'ignored - no message found'})

            message_data = data['message']
            
            # Safety Check 2: Extract data safely using .get()
            # If 'chat' is missing, we can't reply, so we ignore it
            if 'chat' not in message_data:
                return JsonResponse({'status': 'ignored - no chat id'})

            chat_id = message_data['chat']['id']
            text = message_data.get('text', '')
            
            # Handle missing 'from' field (this was your error!)
            from_data = message_data.get('from', {})
            sender_name = from_data.get('first_name', 'Unknown Owner')

            # ------------------------------------------------
            # The rest of the logic logic remains exactly the same
            # ------------------------------------------------

            # 1. Save Raw Message
            customer, _ = Customer.objects.get_or_create(
                chat_id=str(chat_id), 
                defaults={'name': sender_name, 'platform': 'TG'}
            )
            raw_msg = RawMessage.objects.create(
                customer=customer, 
                text=text, 
                meta_data=data
            )

            # 2. Ask AI what to do
            ai_result = parse_order_with_ai(text)
            
            # --- FIX: Force Uppercase ---
            raw_intent = ai_result.get('intent', 'UNKNOWN')
            intent = raw_intent.upper() if raw_intent else 'UNKNOWN'
            # ----------------------------

            print(f"DEBUG: Intent Raw='{raw_intent}', Normalized='{intent}'") # <--- Add this debug line
            
            # Check if AI failed to return a result
            if not ai_result:
                send_telegram_reply(chat_id, "⚠️ Error: AI could not process this message.")
                return JsonResponse({'status': 'ai_error'})

            intent = ai_result.get('intent')

            # ... inside telegram_webhook ...

            # ... inside telegram_webhook ...
            
            # --- SCENARIO A: NEW ORDER ---
            if intent == 'NEW_ORDER':
                items_text = ""
                created_ids = [] 
                
                # DEBUG PRINT: Let's see exactly what the AI sent us
                print(f"DEBUG AI ITEMS: {ai_result.get('items')}")

                for item in ai_result.get('items', []):
                    # --- SAFETY FIX ---
                    # If AI returns a simple string like "Cake", convert it to a dict
                    if isinstance(item, str):
                        item = {
                            'description': item,
                            'quantity': 1,
                            'price': 0,
                            'client_name': 'Unknown'
                        }
                    # ------------------

                    client_name = item.get('client_name', 'Unknown')
                    
                    # Ensure price is a number (sometimes AI sends "200k" as text here)
                    price = item.get('price')
                    if not isinstance(price, int):
                         price = 0 # Default to 0 if invalid

                    order = Order.objects.create(
                        customer=customer,
                        source_message=raw_msg,
                        client_name=client_name,
                        item_description=item.get('description', 'Unknown Item'), # safely get description
                        quantity=item.get('quantity', 1),
                        price=price,
                        due_date=ai_result.get('due_date'),
                        status='PENDING'
                    )
                    created_ids.append(str(order.id))
                    
                    price_display = f"Rp {price:,}" if price else "?"
                    items_text += f"- [ID: {order.id}] {item.get('quantity', 1)}x {item.get('description', 'Item')} ({price_display})\n  👤 {client_name}\n"
                
                ids_str = ", ".join(created_ids)
                reply = f"📝 **Review Order:**\n{items_text}\nDue: {ai_result.get('due_date')}\n\nReply **'Ok {ids_str}'** to confirm."
                send_telegram_reply(chat_id, reply)

            # ... (New Order Logic remains the same) ...

            # --- SCENARIO B: CONFIRMATION ---
            elif intent == 'CONFIRM':
                target_id = ai_result.get('order_id')
                if target_id:
                    orders_to_confirm = Order.objects.filter(id=target_id, customer=customer, status='PENDING')
                else:
                    # Fallback to latest if no ID given (optional, or you can make this strict too)
                    orders_to_confirm = Order.objects.filter(customer=customer, status='PENDING').order_by('-created_at')[:1]

                if orders_to_confirm.exists():
                    for order in orders_to_confirm:
                        order.status = 'CONFIRMED'
                        
                        # --- SYNC TO GOOGLE CALENDAR ---
                        event_id = create_calendar_event(order)
                        if event_id:
                            order.calendar_event_id = event_id # Save the ID for later deletion
                        # -------------------------------

                        order.save()
                        send_telegram_reply(chat_id, f"✅ Order #{order.id} ({order.item_description}) Confirmed & Synced!")
                else:
                    send_telegram_reply(chat_id, "❓ No pending order found to confirm.")

            # --- SCENARIO C: CANCEL (STRICT MODE) ---
            elif intent == 'CANCEL':
                target_id = ai_result.get('order_id')
                
                # REQUIREMENT: Ignore if no ID is present
                if not target_id:
                    send_telegram_reply(chat_id, "⚠️ To cancel, you must provide the ID (e.g., 'Cancel 5').")
                else:
                    # Find order regardless of status (Pending or Confirmed)
                    # We only let them cancel THEIR own orders
                    order_to_cancel = Order.objects.filter(id=target_id, customer=customer).first()
                    
                    if order_to_cancel:
                        # order_to_cancel.status = 'CANCELLED'
                        # order_to_cancel.save()
                        # send_telegram_reply(chat_id, f"❌ Order #{target_id} has been CANCELLED.")
                        
                        # 1. Remove from Google Calendar if exists
                        if order_to_cancel.calendar_event_id:
                            delete_calendar_event(order_to_cancel.calendar_event_id)
                            order_to_cancel.calendar_event_id = None # Clear it

                        # 2. Update DB
                        order_to_cancel.status = 'CANCELLED'
                        order_to_cancel.save()
                        send_telegram_reply(chat_id, f"❌ Order #{target_id} has been CANCELLED and removed from Calendar.")
                    else:
                        send_telegram_reply(chat_id, f"❓ Could not find Order #{target_id}.")

            # ... (inside telegram_webhook) ...

            # --- SCENARIO D: LIST ORDERS (NEXT 3 DAYS) ---
            elif intent == 'LIST_ORDERS':                
                
                today = timezone.localdate()
                end_date = today + timedelta(days=3)
                
                # Filter: Active orders between TODAY and TODAY+3
                orders = Order.objects.filter(
                    customer=customer,
                    due_date__date__range=[today, end_date] 
                ).exclude(status='CANCELLED').order_by('due_date')

                if orders.exists():
                    msg = f"📋 **Orders (Next 3 Days):**\n"
                    current_date_header = None
                    
                    for o in orders:
                        # Group visually by date
                        order_date = o.due_date.strftime('%d %b') # e.g., "27 Dec"
                        if order_date != current_date_header:
                            msg += f"\n📅 *{order_date}*\n"
                            current_date_header = order_date
                        
                        # Icon based on status
                        icon = "✅" if o.status == 'CONFIRMED' else "⏳"
                        
                        # Format: [ID] Who - What
                        msg += f"[{o.id}] {o.client_name} - {o.item_description} ({icon})\n"
                        
                    send_telegram_reply(chat_id, msg)
                else:
                    send_telegram_reply(chat_id, "📅 No active orders found for the next 3 days.")

            # --- SCENARIO E: UNKNOWN ---
            else:
                send_telegram_reply(chat_id, "I didn't understand. Try 'Pesan...', 'Ok [ID]', 'Cancel [ID]', or 'Cek Order'.")

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            # Print the FULL error to the terminal so we can see it
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'method not allowed'}, status=405)