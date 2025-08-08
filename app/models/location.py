from app import db

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    location_type = db.Column(db.String(50))  # e.g., 'warehouse', 'distribution_site', 'office'
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    region = db.Column(db.String(100))
    country = db.Column(db.String(100), default='DRC')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Relations
    waybills_from = db.relationship('Waybill', foreign_keys='Waybill.origin_id', backref='origin', lazy=True)
    waybills_to = db.relationship('Waybill', foreign_keys='Waybill.destination_id', backref='destination', lazy=True)
    distributions = db.relationship('Distribution', backref='location', lazy=True)
    
    def __repr__(self):
        return f'<Location {self.code} - {self.name}>'
