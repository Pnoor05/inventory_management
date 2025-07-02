


'''
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from lib.database import Database

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username, role): 
        self.id = id
        self.username = username
        self.role = role

def setup_login_manager(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return User(user['id'], user['username'], user['role']) if user else None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.list'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)
            return redirect(url_for('products.list'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html') 

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/login.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']
        
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user.id,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], current_pw):
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                         (generate_password_hash(new_pw), current_user.id))
            conn.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('products.list'))
        
        flash('Current password is incorrect', 'danger')
        conn.close()
    
    return render_template('templates.auth/change_password.html')
'''


from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from lib.database import Database

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    def __init__(self, id, username, role): 
        self.id = id
        self.username = username
        self.role = role

def setup_login_manager(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return User(user['id'], user['username'], user['role']) if user else None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('products.list'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember') 
        
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj, remember=bool(remember))
            return redirect(url_for('products.list'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html') 

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('auth/login.html')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form['current_password']
        new_pw = request.form['new_password']
        
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (current_user.id,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], current_pw):
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                         (generate_password_hash(new_pw), current_user.id))
            conn.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('products.list'))
        
        flash('Current password is incorrect', 'danger')
        conn.close()
    
    return render_template('templates.auth/change_password.html')