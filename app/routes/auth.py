from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from app import db
from app.models import User, Role
from app.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.email import send_password_reset_email

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Email ou mot de passe invalide', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.is_active:
            flash('Ce compte a été désactivé', 'warning')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))
        
    return render_template('auth/login.html', title='Connexion', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=form.email.data).first():
            flash('Un compte existe déjà avec cette adresse email', 'warning')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=form.username.data).first():
            flash("Ce nom d'utilisateur est déjà pris", 'warning')
            return redirect(url_for('auth.register'))
            
        # Créer un nouvel utilisateur
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        # Assigner le rôle par défaut (viewer)
        default_role = Role.query.filter_by(name='viewer').first()
        if default_role:
            user.roles.append(default_role)
            
        db.session.add(user)
        db.session.commit()
        
        flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Créer un compte', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Vérifiez votre email pour les instructions de réinitialisation du mot de passe', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password_request.html',
                         title='Réinitialiser le mot de passe',
                         form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Lien de réinitialisation invalide ou expiré', 'warning')
        return redirect(url_for('auth.login'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Votre mot de passe a été réinitialisé avec succès', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form)
