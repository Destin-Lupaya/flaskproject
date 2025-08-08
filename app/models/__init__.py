from .user import User, Role, UserRoles
from .location import Location
from .product import Product, ProductCategory
from .waybill import Waybill, WaybillItem, WaybillStatus
from .distribution import Distribution, DistributionItem, Beneficiary, Household
from .transport import Carrier, Vehicle

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = [
    'User', 'Role', 'UserRoles',
    'Location',
    'Product', 'ProductCategory',
    'Waybill', 'WaybillItem', 'WaybillStatus',
    'Distribution', 'DistributionItem', 'Beneficiary', 'Household',
    'Carrier', 'Vehicle'
]
