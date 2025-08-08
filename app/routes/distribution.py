from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

from app import db
from app.models import (
    Distribution, DistributionItem, Beneficiary, Household, 
    Location, Product, User
)
from app.forms import (
    DistributionForm, DistributionItemForm, BeneficiaryForm, 
    HouseholdForm, DistributionFilterForm
)
from app.decorators import permission_required
from app.utils import generate_distribution_number

bp = Blueprint('distribution', __name__)

@bp.route('/')
@login_required
@permission_required('view_distributions')
def index():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    location_id = request.args.get('location_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Distribution.query
    
    # Filtres
    if status != 'all':
        query = query.filter(Distribution.status == status)
    
    if location_id:
        query = query.filter(Distribution.location_id == location_id)
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Distribution.distribution_date >= start_date)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Distribution.distribution_date < end_date)
        except ValueError:
            pass
    
    # Recherche
    if search:
        search = f'%{search}%'
        query = query.join(Location)
        query = query.filter(
            or_(
                Distribution.distribution_number.ilike(search),
                Location.name.ilike(search),
                Distribution.staff_name.ilike(search)
            )
        )
    
    # Trier par date de distribution décroissante
    distributions = query.order_by(Distribution.distribution_date.desc()).paginate(
        page=page, 
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    # Formulaire de filtre
    filter_form = DistributionFilterForm()
    filter_form.location_id.choices = [(0, 'Tous les sites')] + [
        (loc.id, loc.name) for loc in Location.query.order_by(Location.name).all()
    ]
    filter_form.location_id.data = location_id or 0
    filter_form.status.data = status
    filter_form.start_date.data = start_date
    filter_form.end_date.data = end_date
    
    return render_template('distribution/index.html',
                         distributions=distributions,
                         filter_form=filter_form,
                         search=search)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@permission_required('create_distributions')
def create():
    form = DistributionForm()
    
    # Remplir les choix des champs de sélection
    form.location_id.choices = [(loc.id, loc.name) 
                              for loc in Location.query.order_by(Location.name).all()]
    
    if form.validate_on_submit():
        distribution = Distribution(
            distribution_number=generate_distribution_number(),
            distribution_date=form.distribution_date.data,
            distribution_time=form.distribution_time.data,
            location_id=form.location_id.data,
            distribution_type=form.distribution_type.data,
            status='planned',
            target_beneficiaries=form.target_beneficiaries.data,
            staff_name=form.staff_name.data or current_user.full_name(),
            staff_contact=form.staff_contact.data or current_user.phone,
            notes=form.notes.data,
            created_by=current_user
        )
        
        db.session.add(distribution)
        db.session.commit()
        
        flash(f"La distribution {distribution.distribution_number} a été créée avec succès.", 'success')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    # Définir les valeurs par défaut
    if not form.staff_name.data and current_user:
        form.staff_name.data = current_user.full_name()
    if not form.staff_contact.data and current_user:
        form.staff_contact.data = current_user.phone
    
    return render_template('distribution/form.html',
                         form=form,
                         title='Planifier une distribution')

@bp.route('/<int:distribution_id>')
@login_required
@permission_required('view_distributions')
def detail(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    return render_template('distribution/detail.html',
                         distribution=distribution)

@bp.route('/<int:distribution_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required('edit_distributions')
def edit(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    # Vérifier si la distribution peut être modifiée
    if distribution.status not in ['planned', 'in_progress']:
        flash("Cette distribution ne peut plus être modifiée.", 'warning')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    form = DistributionForm(obj=distribution)
    form.location_id.choices = [(loc.id, loc.name) 
                              for loc in Location.query.order_by(Location.name).all()]
    
    if form.validate_on_submit():
        distribution.distribution_date = form.distribution_date.data
        distribution.distribution_time = form.distribution_time.data
        distribution.location_id = form.location_id.data
        distribution.distribution_type = form.distribution_type.data
        distribution.target_beneficiaries = form.target_beneficiaries.data
        distribution.staff_name = form.staff_name.data
        distribution.staff_contact = form.staff_contact.data
        distribution.notes = form.notes.data
        
        # Mettre à jour le statut si nécessaire
        if request.form.get('action') == 'start' and distribution.status == 'planned':
            distribution.status = 'in_progress'
            flash("La distribution a été marquée comme commencée.", 'success')
        
        db.session.commit()
        flash("Les modifications ont été enregistrées.", 'success')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    return render_template('distribution/form.html',
                         form=form,
                         distribution=distribution,
                         title='Modifier la distribution')

@bp.route('/<int:distribution_id>/complete', methods=['POST'])
@login_required
@permission_required('complete_distributions')
def complete(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    if distribution.status != 'in_progress':
        flash("Seules les distributions en cours peuvent être marquées comme terminées.", 'warning')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    # Mettre à jour le statut
    distribution.status = 'completed'
    distribution.actual_beneficiaries = len(distribution.beneficiaries)
    distribution.updated_by = current_user
    distribution.updated_at = datetime.utcnow()
    
    # Mettre à jour les statistiques des bénéficiaires
    for beneficiary in distribution.beneficiaries:
        beneficiary.last_distribution_date = distribution.distribution_date
    
    db.session.commit()
    
    flash("La distribution a été marquée comme terminée avec succès.", 'success')
    return redirect(url_for('distribution.detail', distribution_id=distribution.id))

@bp.route('/<int:distribution_id>/beneficiaries')
@login_required
@permission_required('view_distributions')
def beneficiaries(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    # Récupérer les bénéficiaires avec leur ménage
    beneficiaries = db.session.query(
        Beneficiary,
        Household
    ).join(
        Household,
        Beneficiary.household
    ).join(
        distribution_beneficiaries,
        Beneficiary.id == distribution_beneficiaries.c.beneficiary_id
    ).filter(
        distribution_beneficiaries.c.distribution_id == distribution_id
    ).order_by(
        Household.household_id,
        Beneficiary.last_name,
        Beneficiary.first_name
    ).all()
    
    return render_template('distribution/beneficiaries.html',
                         distribution=distribution,
                         beneficiaries=beneficiaries)

@bp.route('/<int:distribution_id>/add-beneficiaries', methods=['GET', 'POST'])
@login_required
@permission_required('edit_distributions')
def add_beneficiaries(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    # Vérifier si la distribution peut être modifiée
    if distribution.status not in ['planned', 'in_progress']:
        flash("Les bénéficiaires ne peuvent plus être ajoutés à cette distribution.", 'warning')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    if request.method == 'POST':
        beneficiary_ids = request.form.getlist('beneficiary_ids')
        
        if not beneficiary_ids:
            flash("Veuillez sélectionner au moins un bénéficiaire.", 'warning')
        else:
            # Ajouter les bénéficiaires sélectionnés
            for beneficiary_id in beneficiary_ids:
                beneficiary = Beneficiary.query.get(beneficiary_id)
                if beneficiary and beneficiary not in distribution.beneficiaries:
                    distribution.beneficiaries.append(beneficiary)
            
            # Mettre à jour le nombre de bénéficiaires
            distribution.actual_beneficiaries = len(distribution.beneficiaries)
            db.session.commit()
            
            flash(f"{len(beneficiary_ids)} bénéficiaires ont été ajoutés à la distribution.", 'success')
            return redirect(url_for('distribution.beneficiaries', distribution_id=distribution.id))
    
    # Récupérer les bénéficiaires non encore inclus
    current_beneficiary_ids = [b.id for b in distribution.beneficiaries]
    query = Beneficiary.query.filter_by(is_active=True)
    
    if current_beneficiary_ids:
        query = query.filter(~Beneficiary.id.in_(current_beneficiary_ids))
    
    # Filtrer par recherche si fourni
    search = request.args.get('search', '')
    if search:
        search = f'%{search}%'
        query = query.filter(
            or_(
                Beneficiary.beneficiary_id.ilike(search),
                Beneficiary.first_name.ilike(search),
                Beneficiary.last_name.ilike(search),
                Beneficiary.phone_number.ilike(search)
            )
        )
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    beneficiaries = query.order_by(
        Beneficiary.last_name,
        Beneficiary.first_name
    ).paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('distribution/add_beneficiaries.html',
                         distribution=distribution,
                         beneficiaries=beneficiaries,
                         search=search)

@bp.route('/<int:distribution_id>/items')
@login_required
@permission_required('view_distributions')
def items(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    return render_template('distribution/items.html',
                         distribution=distribution)

@bp.route('/<int:distribution_id>/add-item', methods=['GET', 'POST'])
@login_required
@permission_required('edit_distributions')
def add_item(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    # Vérifier si la distribution peut être modifiée
    if distribution.status not in ['planned', 'in_progress']:
        flash("Les articles ne peuvent plus être ajoutés à cette distribution.", 'warning')
        return redirect(url_for('distribution.detail', distribution_id=distribution.id))
    
    form = DistributionItemForm()
    form.product_id.choices = [(p.id, f"{p.code} - {p.name}") 
                             for p in Product.query.filter_by(is_active=True).order_by(Product.name).all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        if not product:
            flash("Produit non trouvé.", 'danger')
            return redirect(url_for('distribution.items', distribution_id=distribution.id))
        
        # Vérifier si l'article existe déjà
        existing_item = DistributionItem.query.filter_by(
            distribution_id=distribution.id,
            product_id=product.id
        ).first()
        
        if existing_item:
            flash("Ce produit a déjà été ajouté à la distribution.", 'warning')
        else:
            # Créer un nouvel article
            item = DistributionItem(
                distribution_id=distribution.id,
                product_id=product.id,
                planned_quantity=form.planned_quantity.data,
                planned_unit=form.planned_unit.data,
                distributed_quantity=form.distributed_quantity.data or form.planned_quantity.data,
                distributed_unit=form.distributed_unit.data or form.planned_unit.data,
                batch_number=form.batch_number.data,
                expiry_date=form.expiry_date.data,
                notes=form.notes.data
            )
            
            db.session.add(item)
            db.session.commit()
            
            flash(f"L'article {product.name} a été ajouté à la distribution.", 'success')
        
        return redirect(url_for('distribution.items', distribution_id=distribution.id))
    
    return render_template('distribution/item_form.html',
                         form=form,
                         distribution=distribution,
                         title='Ajouter un article')

@bp.route('/<int:distribution_id>/reports')
@login_required
@permission_required('view_reports')
def reports(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    
    # Statistiques de base
    stats = {
        'total_beneficiaries': len(distribution.beneficiaries),
        'total_items': len(distribution.items),
        'total_quantity': sum(item.distributed_quantity for item in distribution.items)
    }
    
    # Détails par produit
    products = []
    for item in distribution.items:
        products.append({
            'name': item.product.name,
            'unit': item.distributed_unit,
            'quantity': item.distributed_quantity,
            'beneficiaries_count': stats['total_beneficiaries']
        })
    
    return render_template('distribution/reports.html',
                         distribution=distribution,
                         stats=stats,
                         products=products)

@bp.route('/<int:distribution_id>/print')
@login_required
@permission_required('view_distributions')
def print_distribution(distribution_id):
    distribution = Distribution.query.get_or_404(distribution_id)
    return render_template('distribution/print.html',
                         distribution=distribution)
