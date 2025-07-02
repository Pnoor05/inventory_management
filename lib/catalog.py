from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import fitz  # PyMuPDF
import re
import os
from werkzeug.utils import secure_filename
from lib.database import Database

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/process_catalog', methods=['POST'])
@login_required
def process():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('products.list'))
    
    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        flash('Only PDF files are accepted', 'error')
        return redirect(url_for('products.list'))
    
    try:
        # Save PDF temporarily
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp_uploads', filename)
        os.makedirs('temp_uploads', exist_ok=True)
        file.save(temp_path)
        
        # Process PDF
        doc = fitz.open(temp_path)
        full_text = "".join([page.get_text() for page in doc])

        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all products for matching
        cursor.execute("""
            SELECT p.id, p.brand, p.description, p.unit_price, c.name as category
            FROM products p JOIN categories c ON p.category_id = c.id
            WHERE p.is_deleted = 0
        """)
        db_products = {f"{p['brand']} {p['description']}": p for p in cursor.fetchall()}

        # Find price changes
        changes = []

        for page in doc:
            text = page.get_text().strip()
            # Look for patterns like "Brand Description ₹Price"
            matches = re.finditer(r'(?P<brand>\w+)\s+(?P<desc>[\w\s]+?)\s+₹(?P<price>\d+\.\d{2})', text)

            for match in matches:
                product_key = f"{match.group('brand')} {match.group('desc')}".strip()
                if product_key in db_products:
                    product = db_products[product_key]
                    new_price = float(match.group('price'))
                    if new_price != product['unit_price']:
                        changes.append({
                            'product_id': product['id'],
                            'display_text': f"{product['brand']} {product['description']}",
                            'old_price': product['unit_price'],
                            'new_price': new_price,
                            'difference': new_price - product['unit_price'],
                            'category': product['category']
                        })
        # Sort changes by impact (largest changes first)
        changes.sort(key=lambda x: abs(x['difference']), reverse=True)
        
        # Store raw changes for approval (no auto-updates)
        if changes:
            # Log processing
            cursor.execute("""
 INSERT INTO catalog_processing_logs
                (filename, processed_by, total_changes, changes_json)
                VALUES (%s, %s, %s, %s)
            """, (filename, current_user.id, len(changes)))
            
        conn.commit()
        return render_template('products/price_review.html', 
                             changes=changes,
                             filename=filename)
        
    except Exception as e:
        flash(f'Error processing PDF: {str(e)}', 'error')
        return redirect(url_for('products.list'))
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        if 'conn' in locals():
            conn.close()


@catalog_bp.route('/apply_price_changes', methods=['POST'])
@login_required
def apply_changes():
    conn = Database.get_connection()
    cursor = conn.cursor()
    
    try:
        updated = 0
        price_history = []
        
        # Process each potential update
        for key in request.form: # Iterate through form keys
            # Check if it's a price field and the corresponding approve checkbox is 'on'
            if key.startswith('price_') and request.form.get(f'approve_{key[7:]}') == 'on':
                product_id = int(key[7:]) # Extract product_id from key
                new_price = float(request.form[key])
                
                # Update product only if price is different, and record in history
                cursor.execute("""
 UPDATE products
                    SET unit_price = %s
                    WHERE id = %s AND unit_price != %s
 """, (new_price, product_id, new_price))

                if cursor.rowcount > 0: # Check if the update actually happened
                    cursor.execute("""
 INSERT INTO price_history # Insert history using SELECT to get old_price
                        (product_id, old_price, new_price, changed_by, source, is_catalog_update)
 SELECT
                            id, # Get id from products table
                            unit_price, # Get old_price from products table before the implicit update above
                            %s, # New price from form
                            %s, # Current user id
 'catalog', # Source
                            TRUE # Is catalog update
                        FROM products # Select from the products table
                        WHERE id = %s # For the specific product
 """, (new_price, current_user.id, product_id))
                    updated += 1 # Increment updated count

        conn.commit() # Commit the transaction if all updates and inserts succeed
        flash(f"Updated {updated} product prices", 'success') # Success message

    except Exception as e: # Catch any errors
        conn.rollback() # Rollback the transaction on error
        flash(f'Price update failed: {str(e)}', 'danger') # Error message
    finally:
        conn.close()
    
    return redirect(url_for('products.list'))