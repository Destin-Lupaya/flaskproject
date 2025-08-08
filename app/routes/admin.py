from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.models import User, Role, UserRoles, Location, Product, ProductCategory, Carrier, Vehicle
from app.forms import (
    UserForm, RoleForm, LocationForm, ProductForm, 
    ProductCategoryForm, CarrierForm, VehicleForm
)
from app.decorators import admin_required, permission_required

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
@admin_required
def index():
    stats = {
        'users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'locations': Location.query.count(),
        'products': Product.query.count(),
        'carriers': Carrier.query.count(),
        'vehicles': Vehicle.query.count()
    }
    return render_template('admin/index.html', stats=stats)

# Gestion des utilisateurs
@bp.route('/users')
@login_required
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    
    if search:
        search = f'%{search}%'
        query = query.filter(
            or_(
                User.username.ilike(search),
                User.email.ilike(search),
                User.first_name.ilike(search),
                User.last_name.ilike(search)
            )
        )
    
    users = query.order_by(User.username).paginate(
        page=page, 
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('admin/users/list.html', users=users, search=search)

@bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def user_create():
    form = UserForm()
    form.roles.choices = [(r.id, r.name) for r in Role.query.order_by('name')]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        # Ajouter les rôles sélectionnés
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f"L'utilisateur {user.username} a été créé avec succès.", 'success')
        return redirect(url_for('admin.user_list'))
        
    return render_template('admin/users/form.html', form=form, title='Créer un utilisateur')

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.roles.choices = [(r.id, r.name) for r in Role.query.order_by('name')]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.set_password(form.password.data)
        
        # Mettre à jour les rôles
        user.roles = []
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)
        
        db.session.commit()
        flash(f"Les informations de l'utilisateur {user.username} ont été mises à jour.", 'success')
        return redirect(url_for('admin.user_list'))
    
    # Pré-sélectionner les rôles actuels
    form.roles.data = [role.id for role in user.roles]
    
    return render_template('admin/users/form.html', form=form, title='Modifier un utilisateur', user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    if current_user.id == user_id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'danger')
        return redirect(url_for('admin.user_list'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f"L'utilisateur {user.username} a été supprimé.", 'success')
    return redirect(url_for('admin.user_list'))

# Gestion des rôles
@bp.route('/roles')
@login_required
@admin_required
def role_list():
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin/roles/list.html', roles=roles)

@bp.route('/roles/create', methods=['GET', 'POST'])
@login_required
@admin_required
def role_create():
    form = RoleForm()
    
    if form.validate_on_submit():
        role = Role(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(role)
        db.session.commit()
        
        flash(f"Le rôle {role.name} a été créé avec succès.", 'success')
        return redirect(url_for('admin.role_list'))
        
    return render_template('admin/roles/form.html', form=form, title='Créer un rôle')

@bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def role_edit(role_id):
    role = Role.query.get_or_404(role_id)
    form = RoleForm(obj=role)
    
    if form.validate_on_submit():
        role.name = form.name.data
        role.description = form.description.data
        
        db.session.commit()
        flash(f"Le rôle {role.name} a été mis à jour.", 'success')
        return redirect(url_for('admin.role_list'))
        
    return render_template('admin/roles/form.html', form=form, title='Modifier un rôle', role=role)

@bp.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@admin_required
def role_delete(role_id):
    role = Role.query.get_or_404(role_id)
    
    # Vérifier si le rôle est utilisé par des utilisateurs
    if role.users.count() > 0:
        flash('Ce rôle est attribué à des utilisateurs et ne peut pas être supprimé.', 'danger')
        return redirect(url_for('admin.role_list'))
    
    db.session.delete(role)
    db.session.commit()
    
    flash(f"Le rôle {role.name} a été supprimé.", 'success')
    return redirect(url_for('admin.role_list'))

# Gestion des emplacements (similaire à la gestion des utilisateurs)
@bp.route('/locations')
@login_required
@permission_required('manage_locations')
def location_list():
    locations = Location.query.order_by(Location.name).all()
    return render_template('admin/locations/list.html', locations=locations)

@bp.route('/locations/create', methods=['GET', 'POST'])
@login_required
@permission_required('manage_locations')
def location_create():
    form = LocationForm()
    
    if form.validate_on_submit():
        location = Location(
            name=form.name.data,
            code=form.code.data,
            location_type=form.location_type.data,
            address=form.address.data,
            city=form.city.data,
            region=form.region.data,
            country=form.country.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            is_active=form.is_active.data,
            notes=form.notes.data
        )
        
        db.session.add(location)
        db.session.commit()
        
        flash(f"L'emplacement {location.name} a été créé avec succès.", 'success')
        return redirect(url_for('admin.location_list'))
        
    return render_template('admin/locations/form.html', form=form, title='Créer un emplacement')

# Les autres vues CRUD pour les emplacements, produits, catégories, transporteurs, etc. suivent le même modèle
# ...

# Exemple pour les produits
@bp.route('/products')
@login_required
@permission_required('manage_products')
def product_list():
    products = Product.query.order_by(Product.name).all()
    return render_template('admin/products/list.html', products=products)

# ... et ainsi de suite pour les autres modèles
