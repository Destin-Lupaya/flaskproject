from app import db

class Carrier(db.Model):
    __tablename__ = 'carriers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    tax_id = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Relations
    vehicles = db.relationship('Vehicle', backref='carrier', lazy=True)
    waybills = db.relationship('Waybill', backref='carrier', lazy=True)
    
    def __repr__(self):
        return f'<Carrier {self.name}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    capacity_kg = db.Column(db.Float)
    capacity_volume = db.Column(db.Float)  # in cubic meters
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    carrier_id = db.Column(db.Integer, db.ForeignKey('carriers.id'))
    waybills = db.relationship('Waybill', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.registration_number}>'
