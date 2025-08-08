from datetime import datetime
from app import db
from sqlalchemy import Enum

class WaybillStatus:
    DRAFT = 'draft'
    IN_TRANSIT = 'in_transit'
    RECEIVED = 'received'
    PARTIALLY_RECEIVED = 'partially_received'
    CANCELLED = 'cancelled'

class Waybill(db.Model):
    __tablename__ = 'waybills'
    
    id = db.Column(db.Integer, primary_key=True)
    waybill_number = db.Column(db.String(50), unique=True, nullable=False)
    reference_number = db.Column(db.String(50))
    batch_number = db.Column(db.String(50))
    status = db.Column(db.Enum(
        WaybillStatus.DRAFT,
        WaybillStatus.IN_TRANSIT,
        WaybillStatus.RECEIVED,
        WaybillStatus.PARTIALLY_RECEIVED,
        WaybillStatus.CANCELLED,
        name='waybill_status'
    ), default=WaybillStatus.DRAFT)
    
    # Dates
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_shipped = db.Column(db.DateTime)
    date_received = db.Column(db.DateTime)
    
    # Relations
    origin_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    carrier_id = db.Column(db.Integer, db.ForeignKey('carriers.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    received_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Driver information
    driver_name = db.Column(db.String(100))
    driver_phone = db.Column(db.String(20))
    
    # Totals
    total_quantity = db.Column(db.Float, default=0.0)
    total_weight_kg = db.Column(db.Float, default=0.0)
    
    # Receipt information
    received_quantity = db.Column(db.Float, default=0.0)
    received_weight_kg = db.Column(db.Float, default=0.0)
    loss_kg = db.Column(db.Float, default=0.0)
    
    # Additional information
    notes = db.Column(db.Text)
    
    # Relations
    items = db.relationship('WaybillItem', backref='waybill', lazy=True, cascade='all, delete-orphan')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    received_by = db.relationship('User', foreign_keys=[received_by_id])
    
    def calculate_totals(self):
        """Calculate and update the total quantities and weights."""
        self.total_quantity = sum(item.quantity_send for item in self.items)
        self.total_weight_kg = sum(item.weight_kg for item in self.items if item.weight_kg)
        
        # Calculate received quantities if any
        if self.status in [WaybillStatus.RECEIVED, WaybillStatus.PARTIALLY_RECEIVED]:
            self.received_quantity = sum(item.quantity_received for item in self.items)
            self.received_weight_kg = sum(item.weight_received_kg for item in self.items if item.weight_received_kg)
            self.loss_kg = max(0, self.total_weight_kg - self.received_weight_kg)
    
    def __repr__(self):
        return f'<Waybill {self.waybill_number}>'

class WaybillItem(db.Model):
    __tablename__ = 'waybill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    waybill_id = db.Column(db.Integer, db.ForeignKey('waybills.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Sent information
    quantity_send = db.Column(db.Float, nullable=False)
    unit_send = db.Column(db.String(20), nullable=False)  # e.g., 'bags', 'cartons', 'units'
    weight_kg = db.Column(db.Float)  # Total weight in kg
    
    # Received information
    quantity_received = db.Column(db.Float)
    unit_received = db.Column(db.String(20))
    weight_received_kg = db.Column(db.Float)
    
    # Quality information
    is_damaged = db.Column(db.Boolean, default=False)
    damage_description = db.Column(db.Text)
    
    # Additional information
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # Relations
    product = db.relationship('Product')
    
    def __repr__(self):
        return f'<WaybillItem {self.id} - {self.product.name} ({self.quantity_send} {self.unit_send})>'
