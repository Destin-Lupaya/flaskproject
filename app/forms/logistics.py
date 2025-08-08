from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, DateField, TimeField, 
    TextAreaField, IntegerField, DecimalField, BooleanField,
    SubmitField, HiddenField, FieldList, FormField, SelectMultipleField
)
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError
from datetime import datetime, date

class WaybillForm(FlaskForm):
    """Formulaire pour créer ou modifier un bordereau d'expédition."""
    reference_number = StringField(
        'Référence',
        validators=[
            Optional(),
            Length(max=50, message="La référence ne doit pas dépasser 50 caractères")
        ]
    )
    batch_number = StringField(
        'Numéro de lot',
        validators=[
            Optional(),
            Length(max=50, message="Le numéro de lot ne doit pas dépasser 50 caractères")
        ]
    )
    origin_id = SelectField(
        'Origine',
        coerce=int,
        validators=[DataRequired(message="L'origine est requise")]
    )
    destination_id = SelectField(
        'Destination',
        coerce=int,
        validators=[DataRequired(message="La destination est requise")]
    )
    carrier_id = SelectField(
        'Transporteur',
        coerce=int,
        validators=[Optional()]
    )
    vehicle_id = SelectField(
        'Véhicule',
        coerce=int,
        validators=[Optional()]
    )
    driver_name = StringField(
        'Nom du chauffeur',
        validators=[
            Optional(),
            Length(max=100, message="Le nom ne doit pas dépasser 100 caractères")
        ]
    )
    driver_phone = StringField(
        'Téléphone du chauffeur',
        validators=[
            Optional(),
            Length(max=20, message="Le numéro de téléphone ne doit pas dépasser 20 caractères")
        ]
    )
    date_shipped = DateTimeField(
        'Date d'expédition',
        validators=[Optional()],
        format='%Y-%m-%dT%H:%M',
        default=datetime.now
    )
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={"rows": 3}
    )
    submit = SubmitField('Enregistrer')


class WaybillItemForm(FlaskForm):
    """Formulaire pour ajouter ou modifier un article dans un bordereau."""
    product_id = SelectField(
        'Produit',
        coerce=int,
        validators=[DataRequired(message="Le produit est requis")]
    )
    quantity_send = DecimalField(
        'Quantité',
        validators=[
            DataRequired(message="La quantité est requise"),
            NumberRange(min=0.001, message="La quantité doit être supérieure à 0")
        ],
        places=3,
        default=1
    )
    unit_send = SelectField(
        'Unité',
        choices=[
            ('kg', 'Kilogramme (kg)'),
            ('g', 'Gramme (g)'),
            ('l', 'Litre (l)'),
            ('ml', 'Millilitre (ml)'),
            ('unit', 'Unité'),
            ('box', 'Boîte'),
            ('bag', 'Sac'),
            ('carton', 'Carton')
        ],
        validators=[DataRequired(message="L'unité est requise")],
        default='kg'
    )
    batch_number = StringField(
        'Numéro de lot',
        validators=[
            Optional(),
            Length(max=50, message="Le numéro de lot ne doit pas dépasser 50 caractères")
        ]
    )
    expiry_date = DateField(
        'Date d'expiration',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={"rows": 2}
    )


class WaybillReceiveForm(FlaskForm):
    """Formulaire pour la réception d'un bordereau."""
    date_received = DateTimeField(
        'Date de réception',
        validators=[DataRequired(message="La date de réception est requise")],
        format='%Y-%m-%dT%H:%M',
        default=datetime.now
    )
    received_by = StringField(
        'Reçu par',
        validators=[
            DataRequired(message="Le nom de la personne qui reçoit est requis"),
            Length(max=100, message="Le nom ne doit pas dépasser 100 caractères")
        ]
    )
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={"rows": 3}
    )
    submit = SubmitField('Valider la réception')


class WaybillItemReceiveForm(FlaskForm):
    """Formulaire pour la réception d'un article d'un bordereau."""
    quantity_received = DecimalField(
        'Quantité reçue',
        validators=[
            DataRequired(message="La quantité reçue est requise"),
            NumberRange(min=0, message="La quantité ne peut pas être négative")
        ],
        places=3
    )
    unit_received = SelectField(
        'Unité',
        choices=[
            ('kg', 'Kilogramme (kg)'),
            ('g', 'Gramme (g)'),
            ('l', 'Litre (l)'),
            ('ml', 'Millilitre (ml)'),
            ('unit', 'Unité'),
            ('box', 'Boîte'),
            ('bag', 'Sac'),
            ('carton', 'Carton')
        ],
        validators=[DataRequired(message="L'unité est requise")]
    )
    is_damaged = BooleanField('Endommagé')
    damage_description = TextAreaField(
        'Description des dommages',
        validators=[Optional()],
        render_kw={"rows": 2, "disabled": True}
    )
    notes = TextAreaField(
        'Notes',
        validators=[Optional()],
        render_kw={"rows": 2}
    )


class WaybillFilterForm(FlaskForm):
    """Formulaire de filtrage des bordereaux."""
    status = SelectField(
        'Statut',
        choices=[
            ('all', 'Tous les statuts'),
            ('draft', 'Brouillon'),
            ('in_transit', 'En transit'),
            ('partially_received', 'Partiellement reçu'),
            ('received', 'Reçu'),
            ('cancelled', 'Annulé')
        ],
        default='all'
    )
    origin_id = SelectField(
        'Origine',
        coerce=int,
        default=0
    )
    destination_id = SelectField(
        'Destination',
        coerce=int,
        default=0
    )
    carrier_id = SelectField(
        'Transporteur',
        coerce=int,
        default=0
    )
    start_date = DateField(
        'Date de début',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    end_date = DateField(
        'Date de fin',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    search = StringField('Recherche')
    submit = SubmitField('Filtrer')

    def __init__(self, *args, **kwargs):
        super(WaybillFilterForm, self).__init__(*args, **kwargs)
        # Ces choix seront remplis dynamiquement dans la vue
        self.origin_id.choices = [(0, 'Toutes les origines')]
        self.destination_id.choices = [(0, 'Toutes les destinations')]
        self.carrier_id.choices = [(0, 'Tous les transporteurs')]
