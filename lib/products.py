'''


from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from lib.database import Database
from flask import jsonify
from flask_login import current_user
import mysql.connector
from flask import current_app



products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
@login_required
def list():
    view_deleted = request.args.get('view_deleted', 0, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Base count query
        count_query = """
            SELECT COUNT(*) as total 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = %s
        """
        params = [view_deleted]
        
        # Base data query
        data_query = """
            SELECT p.*, c.name as category 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = %s
        """
        
        # Add filters
        if search:
            count_query += " AND (p.description LIKE %s OR p.brand LIKE %s)"
            data_query += " AND (p.description LIKE %s OR p.brand LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        if category:
            count_query += " AND c.name = %s"
            data_query += " AND c.name = %s"
            params.append(category)
        
        # Get total count
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        total_pages = (total + per_page - 1) // per_page
        
        # Get paginated data
        data_query += " LIMIT %s OFFSET %s"
        cursor.execute(data_query, params + [per_page, (page - 1) * per_page])
        products = cursor.fetchall()
        
        # Get categories for filter dropdown
        cursor.execute("SELECT name FROM categories")
        categories = [c['name'] for c in cursor.fetchall()]
    
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('products.list'))
    finally:
        if conn and conn.is_connected():
            conn.close()

    
    return render_template('products/list.html',
        products=products,
        categories=categories,
        view_deleted=view_deleted,
        search_query=search,
        category_filter=category,
        current_page=page,
        total_pages=total_pages,
        total_products=total
    )

# In products.py - keep only this one update_price route
@products_bp.route('/update_price/<int:product_id>', methods=['POST'])
@login_required
def update_price(product_id):
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        # Get current price first if you need to log changes
        cursor.execute("SELECT unit_price FROM products WHERE id = %s", (product_id,))
        old_price = cursor.fetchone()[0]
        
        # Update quantity
        cursor.execute("""
            UPDATE products 
            SET quantity_in_stock = %s 
            WHERE id = %s
        """, (data['quantity'], product_id))
        
        # If you also need to update price:
        if 'price' in data:
            cursor.execute("""
                UPDATE products 
                SET unit_price = %s 
                WHERE id = %s
            """, (data['price'], product_id))
            
            # Log price change
            cursor.execute("""
                INSERT INTO price_history 
                (product_id, old_price, new_price, changed_by, source)
                VALUES (%s, %s, %s, %s, 'manual')
            """, (product_id, old_price, data['price'], current_user.id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Insert product
            cursor.execute("""
                INSERT INTO products 
                (category_id, description, brand, unit_price, quantity_in_stock) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                request.form['category_id'],
                request.form['description'],
                request.form['brand'],
                request.form['unit_price'],
                request.form['quantity_in_stock']
            ))
            
            product_id = cursor.lastrowid
            
            # Handle specifications
            category_name = request.form.get('category_name')
            if category_name:
                # Your original spec handling logic here
                pass
            
            conn.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('products.list'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
        finally:
            conn.close()
    
    # GET request
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()
    
    return render_template('products/add.html', categories=categories)

@products_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    # ... existing edit code ...
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE products SET
                description = %s,
                brand = %s,
                unit_price = %s,
                quantity_in_stock = %s
                WHERE id = %s
            """, (
                request.form['description'],
                request.form['brand'],
                request.form['unit_price'],
                request.form['quantity_in_stock'],
                product_id
            ))
            
            conn.commit()
            flash('Product updated!', 'success')
            return redirect(url_for('products.list'))
        except Exception as e:
            conn.rollback()
            flash(f'Update failed: {str(e)}', 'danger')
        finally:
            conn.close()
    
    # GET request
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.list'))
    
    return render_template('products/edit.html', product=product)

@products_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_deleted = 1 WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products.list'))

@products_bp.route('/restore_product/<int:product_id>', methods=['POST'])
@login_required
def restore(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_deleted = 0 WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products.list'))

@products_bp.route('/api/price_history/<int:product_id>')
@login_required
def price_history(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ph.*, u.username 
        FROM price_history ph
        LEFT JOIN users u ON ph.changed_by = u.id
        WHERE product_id = %s 
        ORDER BY changed_at DESC
        LIMIT 50
    """, (product_id,))
    history = cursor.fetchall()
    conn.close()
    return jsonify(history)  # Make sure to return jsonify



@products_bp.route('/get_specifications')
@login_required
def get_specifications():
    category_id = request.args.get('category_id')
    if not category_id:
        return jsonify({'error': 'Missing category_id'}), 400
    
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get category name
        cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Get specifications for this category
        spec_table = f"{category['name'].lower()}_specifications"
        
        try:
            cursor.execute(f"SHOW COLUMNS FROM {spec_table}")
            columns = [col['Field'] for col in cursor.fetchall() if col['Field'] != 'id']
            
            specs = []
            for col in columns:
                specs.append({
                    'name': col,
                    'label': col.replace('_', ' ').title(),
                    'required': True
                })
            
            return jsonify(specs)
        except mysql.connector.Error as e:
            if e.errno == 1146:  # Table doesn't exist
                return jsonify([])  # No specifications for this category
            raise
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@products_bp.route('/update_quantity/<int:product_id>', methods=['POST'])
@login_required
def update_quantity(product_id):
    # Validate request
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Invalid content type'}), 400
    
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Missing quantity parameter'}), 400
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity < 0:
            return jsonify({'success': False, 'error': 'Quantity cannot be negative'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400
    
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get current product data
        cursor.execute("""
            SELECT p.quantity_in_stock, p.min_stock_level, c.name as category 
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        current_qty = product['quantity_in_stock']
        
        # Only proceed if quantity actually changed
        if current_qty == quantity:
            return jsonify({
                'success': True,
                'new_quantity': quantity,
                'message': 'Quantity unchanged'
            })
        
        # Update quantity
        cursor.execute("""
            UPDATE products 
            SET quantity_in_stock = %s 
            WHERE id = %s
        """, (quantity, product_id))
        
        # Log the change in inventory_history (if table exists)
        try:
            cursor.execute("""
                INSERT INTO inventory_history 
                (product_id, field_changed, old_value, new_value, changed_by)
                VALUES (%s, 'quantity_in_stock', %s, %s, %s)
            """, (product_id, current_qty, quantity, current_user.id))
        except mysql.connector.Error as e:
            if e.errno == 1146:  # Table doesn't exist
                pass  # Skip logging if table doesn't exist
            else:
                raise  # Re-raise other errors
        
        # Check stock level and log if below minimum
        if quantity < product['min_stock_level']:
            try:
                cursor.execute("""
                    INSERT INTO stock_alerts
                    (product_id, current_quantity, min_quantity, alerted_by)
                    VALUES (%s, %s, %s, %s)
                """, (product_id, quantity, product['min_stock_level'], current_user.id))
            except mysql.connector.Error as e:
                if e.errno != 1146:  # Ignore if table doesn't exist
                    raise
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'new_quantity': quantity,
            'is_low_stock': quantity < product['min_stock_level'],
            'category': product['category']
        })
        
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating quantity: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
    finally:
        cursor.close()
        conn.close()



@products_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Check if category already exists
        cursor.execute("SELECT id FROM categories WHERE name = %s", (data['name'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category already exists'}), 400
        
        # Insert new category
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (data['name'],))
        category_id = cursor.lastrowid
        
        # Create specifications table if needed
        if data.get('type') and data['type'] != 'standard':
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {data['type']}_specifications (
                        id INT PRIMARY KEY,
                        FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
                    )
                """)
            except Exception as e:
                conn.rollback()
                return jsonify({'success': False, 'error': f'Failed to create specs table: {str(e)}'}), 500
        
        conn.commit()
        return jsonify({'success': True, 'id': category_id, 'name': data['name']})
        
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

            '''
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from lib.database import Database
from flask import jsonify
from flask_login import current_user
import mysql.connector
from flask import current_app

products_bp = Blueprint('products', __name__)
@products_bp.route('/landing_search')
def landing_search():
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    conn = None
    cursor = None

    if not query or len(query) < 2:
        return jsonify(results=[])

    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch product suggestions
        cursor.execute("""
            SELECT 
                p.id,
                p.brand,
                p.description,
                p.unit_price as price,
                p.quantity_in_stock as stock,
                c.name as category
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = 0
            AND (p.description LIKE %s OR p.brand LIKE %s)
            ORDER BY 
                CASE 
                    WHEN p.quantity_in_stock > 0 THEN 0 
                    ELSE 1 
                END,
                p.description ASC
            LIMIT %s
        """, [f"%{query}%", f"%{query}%", limit])
        results = cursor.fetchall()
        
        # Fetch brand suggestions
        cursor.execute("SELECT DISTINCT brand FROM products WHERE brand LIKE %s LIMIT %s", 
                      [f"%{query}%", limit])
        brand_results = cursor.fetchall()
        
        # Combine and format suggestions
        brand_suggestions = [{'brand': b['brand'], 'type': 'brand', 'description': None} 
                           for b in brand_results]
        product_suggestions = [{**p, 'type': 'product'} for p in results]
        
        # Ensure price is float in product suggestions
        for item in product_suggestions:
            if 'price' in item and item['price'] is not None:
                try:
                    item['price'] = float(item['price'])
                except (ValueError, TypeError):
                    item['price'] = 0.0  # Default value for invalid prices
        
        all_suggestions = brand_suggestions + product_suggestions
        return jsonify(results=all_suggestions[:limit])

    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@products_bp.route('/products')
@login_required
def list():
    view_deleted = request.args.get('view_deleted', 0, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    filter_type = request.args.get('filter_type')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Base count query
        count_query = """
            SELECT COUNT(*) as total 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = %s
        """
        params = [view_deleted]
        
        # Base data query
        data_query = """
            SELECT p.*, c.name as category 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = %s
        """
        
        # Add filters
        if search:
            if filter_type == 'brand':
                count_query += " AND p.brand LIKE %s"
                data_query += " AND p.brand LIKE %s"
                params.append(f"%{search}%")
            else: # Default or product search
                count_query += " AND (p.description LIKE %s OR p.brand LIKE %s)"
                data_query += " AND (p.description LIKE %s OR p.brand LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])

        if category:
            count_query += " AND c.name = %s"
            data_query += " AND c.name = %s"
            params.append(category)
        
        # Get total count
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        total_pages = (total + per_page - 1) // per_page
        
        # Get paginated data
        data_query += " LIMIT %s OFFSET %s"
        cursor.execute(data_query, params + [per_page, (page - 1) * per_page])
        products = cursor.fetchall()
        
        # Get categories for filter dropdown
        cursor.execute("SELECT name FROM categories")
        categories = [c['name'] for c in cursor.fetchall()]
    
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('products.list'))
    finally:
        if conn and conn.is_connected():
            conn.close()

    # If it's an AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'products': products,
            'current_page': page,
            'total_pages': total_pages,
            'total_products': total
        })

    
    return render_template('products/list.html',
        products=products,
        categories=categories,
        view_deleted=view_deleted,
        search_query=search,
        category_filter=category,
        current_page=page,
        total_pages=total_pages,
        total_products=total
    )

# In products.py - keep only this one update_price route
@products_bp.route('/update_price/<int:product_id>', methods=['POST'])
@login_required
def update_price(product_id):
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    conn = Database.get_connection()
    cursor = conn.cursor()
    try:
        # Get current price first if you need to log changes
        cursor.execute("SELECT unit_price FROM products WHERE id = %s", (product_id,))
        old_price = cursor.fetchone()[0]
        
        # Update quantity
        cursor.execute("""
            UPDATE products 
            SET quantity_in_stock = %s 
            WHERE id = %s
        """, (data['quantity'], product_id))
        
        # If you also need to update price:
        if 'price' in data:
            cursor.execute("""
                UPDATE products 
                SET unit_price = %s 
                WHERE id = %s
            """, (data['price'], product_id))
            
            # Log price change
            cursor.execute("""
                INSERT INTO price_history 
                (product_id, old_price, new_price, changed_by, source)
                VALUES (%s, %s, %s, %s, 'manual')
            """, (product_id, old_price, data['price'], current_user.id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Insert product
            cursor.execute("""
                INSERT INTO products 
                (category_id, description, brand, unit_price, quantity_in_stock) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                request.form['category_id'],
                request.form['description'],
                request.form['brand'],
                request.form['unit_price'],
                request.form['quantity_in_stock']
            ))
            
            product_id = cursor.lastrowid
            
            # Handle specifications
            category_name = request.form.get('category_name')
            if category_name:
                # Your original spec handling logic here
                pass
            
            conn.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('products.list'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error adding product: {str(e)}', 'danger')
        finally:
            conn.close()
    
    # GET request
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()
    
    return render_template('products/add.html', categories=categories)

@products_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    # ... existing edit code ...
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE products SET
                description = %s,
                brand = %s,
                unit_price = %s,
                quantity_in_stock = %s
                WHERE id = %s
            """, (
                request.form['description'],
                request.form['brand'],
                request.form['unit_price'],
                request.form['quantity_in_stock'],
                product_id
            ))
            
            conn.commit()
            flash('Product updated!', 'success')
            return redirect(url_for('products.list'))
        except Exception as e:
            conn.rollback()
            flash(f'Update failed: {str(e)}', 'danger')
        finally:
            conn.close()
    
    # GET request
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        flash('Product not found', 'danger')
        return redirect(url_for('products.list'))
    
    return render_template('products/edit.html', product=product)

@products_bp.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_deleted = 1 WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products.list'))

@products_bp.route('/restore_product/<int:product_id>', methods=['POST'])
@login_required
def restore(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_deleted = 0 WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products.list'))

@products_bp.route('/api/price_history/<int:product_id>')
@login_required
def price_history(product_id):
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ph.*, u.username 
        FROM price_history ph
        LEFT JOIN users u ON ph.changed_by = u.id
        WHERE product_id = %s 
        ORDER BY changed_at DESC
        LIMIT 50
    """, (product_id,))
    history = cursor.fetchall()
    conn.close()
    return jsonify(history)  # Make sure to return jsonify



@products_bp.route('/get_specifications')
@login_required
def get_specifications():
    category_id = request.args.get('category_id')
    if not category_id:
        return jsonify({'error': 'Missing category_id'}), 400
    
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get category name
        cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        # Get specifications for this category
        spec_table = f"{category['name'].lower()}_specifications"
        
        try:
            cursor.execute(f"SHOW COLUMNS FROM {spec_table}")
            columns = [col['Field'] for col in cursor.fetchall() if col['Field'] != 'id']
            
            specs = []
            for col in columns:
                specs.append({
                    'name': col,
                    'label': col.replace('_', ' ').title(),
                    'required': True
                })
            
            return jsonify(specs)
        except mysql.connector.Error as e:
            if e.errno == 1146:  # Table doesn't exist
                return jsonify([])  # No specifications for this category
            raise
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@products_bp.route('/update_quantity/<int:product_id>', methods=['POST'])
@login_required
def update_quantity(product_id):
    # Validate request
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Invalid content type'}), 400
    
    data = request.get_json()
    if not data or 'quantity' not in data:
        return jsonify({'success': False, 'error': 'Missing quantity parameter'}), 400
    
    # Validate quantity
    try:
        quantity = int(data['quantity'])
        if quantity < 0:
            return jsonify({'success': False, 'error': 'Quantity cannot be negative'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid quantity value'}), 400
    
    conn = Database.get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get current product data
        cursor.execute("""
            SELECT p.quantity_in_stock, p.min_stock_level, c.name as category 
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """, (product_id,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        current_qty = product['quantity_in_stock']
        
        # Only proceed if quantity actually changed
        if current_qty == quantity:
            return jsonify({
                'success': True,
                'new_quantity': quantity,
                'message': 'Quantity unchanged'
            })
        
        # Update quantity
        cursor.execute("""
            UPDATE products 
            SET quantity_in_stock = %s 
            WHERE id = %s
        """, (quantity, product_id))
        
        # Log the change in inventory_history (if table exists)
        try:
            cursor.execute("""
                INSERT INTO inventory_history 
                (product_id, field_changed, old_value, new_value, changed_by)
                VALUES (%s, 'quantity_in_stock', %s, %s, %s)
            """, (product_id, current_qty, quantity, current_user.id))
        except mysql.connector.Error as e:
            if e.errno == 1146:  # Table doesn't exist
                pass  # Skip logging if table doesn't exist
            else:
                raise  # Re-raise other errors
        
        # Check stock level and log if below minimum
        if quantity < product['min_stock_level']:
            try:
                cursor.execute("""
                    INSERT INTO stock_alerts
                    (product_id, current_quantity, min_quantity, alerted_by)
                    VALUES (%s, %s, %s, %s)
                """, (product_id, quantity, product['min_stock_level'], current_user.id))
            except mysql.connector.Error as e:
                if e.errno != 1146:  # Ignore if table doesn't exist
                    raise
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'new_quantity': quantity,
            'is_low_stock': quantity < product['min_stock_level'],
            'category': product['category']
        })
        
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating quantity: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
    finally:
        cursor.close()
        conn.close()



@products_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    conn = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Check if category already exists
        cursor.execute("SELECT id FROM categories WHERE name = %s", (data['name'],))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Category already exists'}), 400
        
        # Insert new category
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (data['name'],))
        category_id = cursor.lastrowid
        
        # Create specifications table if needed
        if data.get('type') and data['type'] != 'standard':
            try:
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {data['type']}_specifications (
                        id INT PRIMARY KEY,
                        FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
                    )
                """)
            except Exception as e:
                conn.rollback()
                return jsonify({'success': False, 'error': f'Failed to create specs table: {str(e)}'}), 500
        
        conn.commit()
        return jsonify({'success': True, 'id': category_id, 'name': data['name']})
        
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()