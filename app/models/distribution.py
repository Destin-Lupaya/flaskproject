from datetime import datetime
from app import db

class Household(db.Model):
    __tablename__ = 'households'
    
    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.String(50), unique=True, nullable=False)
    head_of_household = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.Text)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    gps_coordinates = db.Column(db.String(50))
    registration_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    
    # Relations
    beneficiaries = db.relationship('Beneficiary', backref='household', lazy=True)
    distributions = db.relationship('Distribution', secondary='distribution_beneficiaries', 
                                   back_populates='households')
    
    def __repr__(self):
        return f'<Household {self.household_id} - {self.head_of_household}>'

class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    
    id = db.Column(db.Integer, primary_key=True)
    beneficiary_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # 'male', 'female', 'other'
    phone_number = db.Column(db.String(20))
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=False)
    relationship_to_head = db.Column(db.String(50))
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    registration_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relations
    distributions = db.relationship('Distribution', secondary='distribution_beneficiaries',
                                  back_populates='beneficiaries')
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Beneficiary {self.beneficiary_id} - {self.full_name()}>'

# Association table for many-to-many relationship between Distribution and Beneficiary
distribution_beneficiaries = db.Table('distribution_beneficiaries',
    db.Column('distribution_id', db.Integer, db.ForeignKey('distributions.id'), primary_key=True),
    db.Column('beneficiary_id', db.Integer, db.ForeignKey('beneficiaries.id'), primary_key=True),
    db.Column('household_id', db.Integer, db.ForeignKey('households.id'))
)

class Distribution(db.Model):
    __tablename__ = 'distributions'
    
    id = db.Column(db.Integer, primary_key=True)
    distribution_number = db.Column(db.String(50), unique=True, nullable=False)
    distribution_date = db.Column(db.Date, nullable=False)
    distribution_time = db.Column(db.Time)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    distribution_type = db.Column(db.String(50))  # e.g., 'food', 'non_food', 'cash'
    status = db.Column(db.String(20), default='planned')  # 'planned', 'in_progress', 'completed', 'cancelled'
    
    # Target information
    target_beneficiaries = db.Column(db.Integer, default=0)
    actual_beneficiaries = db.Column(db.Integer, default=0)
    
    # Staff information
    staff_name = db.Column(db.String(100))
    staff_contact = db.Column(db.String(50))
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    items = db.relationship('DistributionItem', backref='distribution', lazy=True, cascade='all, delete-orphan')
    beneficiaries = db.relationship('Beneficiary', secondary='distribution_beneficiaries',
                                  back_populates='distributions')
    households = db.relationship('Household', secondary='distribution_beneficiaries',
                               back_populates='distributions')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    
    def calculate_beneficiary_count(self):
        """Calculate the actual number of beneficiaries served."""
        self.actual_beneficiaries = len(self.beneficiaries)
    
    def __repr__(self):
        return f'<Distribution {self.distribution_number} - {self.distribution_date}>'

class DistributionItem(db.Model):
    __tablename__ = 'distribution_items'
    
    id = db.Column(db.Integer, primary_key=True)
    distribution_id = db.Column(db.Integer, db.ForeignKey('distributions.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Planned quantities
    planned_quantity = db.Column(db.Float, nullable=False)
    planned_unit = db.Column(db.String(20), nullable=False)  # e.g., 'kg', 'g', 'L', 'unit'
    
    # Distributed quantities
    distributed_quantity = db.Column(db.Float)
    distributed_unit = db.Column(db.String(20))
    
    # Additional information
    batch_number = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # Relations
    product = db.relationship('Product')
    
    def __repr__(self):
        return f'<DistributionItem {self.id} - {self.product.name} ({self.planned_quantity} {self.planned_unit})>'
