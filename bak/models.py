from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Numeric, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid
import enum
from datetime import datetime

Base = declarative_base()

# 1. Define the Order Status Enum
# This restricts the status to only these three options, preventing typos like "Canceled" vs "Cancelled"
class OrderStatus(enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

# 2. Raw Logs Table
class RawLog(Base):
    __tablename__ = 'raw_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)  # e.g., "whatsapp", "telegram"
    payload = Column(JSONB, nullable=False)      # Stores the full JSON from the chat app
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to Order (One log might create one order)
    order = relationship("Order", back_populates="raw_log", uselist=False)

# 3. Customers Table
class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    phone_number = Column(String(50), unique=True, index=True, nullable=False)
    default_address = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: One customer has many orders
    orders = relationship("Order", back_populates="customer")

# 4. Orders Table (The Core)
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True) # This acts as your "Order Number" (e.g., 1, 2, 3)
    
    # Links
    raw_log_id = Column(UUID(as_uuid=True), ForeignKey('raw_logs.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    
    # Order Details
    items_summary = Column(Text, nullable=False)    # e.g. "2x Choco Cake"
    total_price = Column(Numeric(10, 2), default=0.00) # Numeric is better for money than Float
    delivery_address = Column(Text, nullable=True)
    
    # Timing
    due_datetime = Column(DateTime, nullable=False) # When the calendar event is set for
    
    # Technical Fields for Logic
    calendar_event_id = Column(String(255), nullable=True) # CRITICAL: Needed to delete/edit the Google Event later
    status = Column(Enum(OrderStatus), default=OrderStatus.ACTIVE)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    raw_log = relationship("RawLog", back_populates="order")