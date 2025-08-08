from app import db

class ProductCategory(db.Model):
    __tablename__ = 'product_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    products = db.relationship('Product', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<ProductCategory {self.code} - {self.name}>'

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'), nullable=False)
    unit_of_measure = db.Column(db.String(20))  # e.g., 'kg', 'g', 'L', 'unit'
    unit_weight_kg = db.Column(db.Float)  # Weight of one unit in kg (for conversion to tons)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    waybill_items = db.relationship('WaybillItem', backref='product', lazy=True)
    distribution_items = db.relationship('DistributionItem', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.code} - {self.name}>'
