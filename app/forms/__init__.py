from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField, SelectMultipleField, DateField,
    TimeField, DateTimeField, DecimalField, IntegerField,
    FieldList, FormField, HiddenField, FileField, RadioField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import TextArea

# Import des formulaires individuels
from .auth import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from .distribution import (
    DistributionForm, DistributionItemForm, BeneficiaryForm, 
    HouseholdForm, DistributionFilterForm, BeneficiarySearchForm
)
from .logistics import (
    WaybillForm, WaybillItemForm, WaybillReceiveForm, 
    WaybillItemReceiveForm, WaybillFilterForm
)
from .admin import (
    UserForm, RoleForm, LocationForm, ProductForm, 
    ProductCategoryForm, CarrierForm, VehicleForm
)

# Ce fichier permet d'importer tous les formulaires depuis un seul endroit
