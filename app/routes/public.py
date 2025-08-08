from flask import Blueprint, render_template, current_app
from flask_login import current_user
from sqlalchemy import func

from app.models import (
    Distribution, Location, Waybill, Beneficiary, Product
)

bp = Blueprint('public', __name__)

@bp.route('/')
def index():
    # Récupérer les statistiques pour la page d'accueil
    stats = {
        'total_beneficiaries': Beneficiary.query.filter_by(is_active=True).count(),
        'total_distributions': Distribution.query.count(),
        'total_sites': Location.query.filter_by(is_active=True).count(),
        'total_products': Product.query.filter_by(is_active=True).count()
    }
    
    # Dernières distributions
    recent_distributions = Distribution.query.order_by(
        Distribution.distribution_date.desc()
    ).limit(3).all()
    
    return render_template('public/index.html', 
                         stats=stats, 
                         recent_distributions=recent_distributions)

@bp.route('/about')
def about():
    return render_template('public/about.html')

@bp.route('/operations')
def operations():
    return render_template('public/operations.html')

@bp.route('/impact')
def impact():
    # Récupérer les statistiques d'impact
    impact_stats = {
        'beneficiaries_served': Beneficiary.query.filter_by(is_active=True).count(),
        'households_reached': 0,  # À implémenter
        'food_distributed': 0,    # À implémenter
        'locations_covered': Location.query.filter_by(is_active=True).count()
    }
    
    # Derniers témoignages (à implémenter)
    testimonials = []
    
    return render_template('public/impact.html', 
                         stats=impact_stats, 
                         testimonials=testimonials)

@bp.route('/contact')
def contact():
    return render_template('public/contact.html')

@bp.route('/partners')
def partners():
    return render_template('public/partners.html')

@bp.route('/privacy')
def privacy():
    return render_template('public/privacy.html')

@bp.route('/terms')
def terms():
    return render_template('public/terms.html')
