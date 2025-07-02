from flask import Blueprint, request, jsonify
from lib.database import Database
from flask_login import current_user
import os
import json
from datetime import datetime
import uuid
import sys
from werkzeug.utils import secure_filename

# Define the folder where files will be stored
# TODO: Update this to a valid path where you want to store uploaded assets.
UPLOAD_FOLDER = 'uploads'

# Define allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'pdf', 'docx'}

def allowed_file(filename):
    """Checks if a file's extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Define the standard variables
STANDARD_VARS = {
    'invoice_id': {'type': 'text', 'sample': 'INV-2023-001'},
    'date': {'type': 'date', 'sample': '2025-05-11'},
    'items': {'type': 'table', 'sample': '[{"name": "Product A", "price": 10.0, "quantity": 2}]'}
}

def render_template(template_html, variables):
    """
    Render the template by replacing dynamic variables with real values.
    """
    for key, value in variables.items():
        placeholder = f'{{{{ {key} }}}}'
        template_html = template_html.replace(placeholder, str(value))
    return template_html

temp_bp = Blueprint('temp_bp', __name__)

# Get temporary bills for a user
@temp_bp.route('/active', methods=['GET'])
def get_active_temp_bills():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    user_id = current_user.id
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM temporary_bills WHERE user_id = %s AND status = 'active'", (user_id,))
        bills = cursor.fetchall()
        return jsonify(bills)
    except Exception as e:
        print(f"Error fetching active temporary bills: {e}", file=sys.stderr)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn and conn.is_connected(): conn.close()

# Get all templates for a user
@temp_bp.route('/api/clients/search', methods=['GET'])
def search_clients():
    search_term = request.args.get('q', '')
    if not search_term or len(search_term) < 2:
        return jsonify([])

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, phone 
            FROM clients 
            WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
            LIMIT 10
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

        clients = cursor.fetchall()
        return jsonify(clients)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@temp_bp.route('/api/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, phone 
            FROM clients 
            WHERE id = %s
        """, (client_id,))

        client = cursor.fetchone()
        if not client:
            return jsonify({'error': 'Client not found'}), 404

        return jsonify(client)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@temp_bp.route('/templates', methods=['GET'])
def get_templates():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    user_id = current_user.id
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bill_templates WHERE user_id = %s", (user_id,))
        templates = cursor.fetchall()
        return jsonify(templates)

    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@temp_bp.route('/api/temp_bills/<int:bill_id>/discount', methods=['POST', 'DELETE'])
def manage_tax(bill_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        # Verify bill ownership
        cursor.execute("SELECT user_id FROM temporary_bills WHERE id = %s", (bill_id,))
        bill = cursor.fetchone()
        if not bill or bill['user_id'] != current_user.id:
            return jsonify({"error": "Not found or unauthorized"}), 404
        if request.method == 'POST':
            tax = request.json
            cursor.execute("""
                UPDATE temporary_bills
                SET bill_data = JSON_SET(
                    bill_data,
                    '$.tax',
                    JSON_OBJECT(
                        'name', %s,
                        'rate', %s,
                        'inclusive', %s
                    )
                )
                WHERE id = %s
            """, (
                tax.get('name'),
                tax.get('rate'),
                tax.get('inclusive', False),
                bill_id
            ))
            action = "added"
        else:  # DELETE
            cursor.execute("""
                UPDATE temporary_bills
                SET bill_data = JSON_REMOVE(bill_data, '$.tax')
                WHERE id = %s
            """, (bill_id,))
            action = "removed"

        conn.commit()
        return jsonify({"message": f"Tax {action} successfully."})

    except Exception as e:
        print("Tax error:", e)
        return jsonify({"error": "Something went wrong"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@temp_bp.route('/api/temp_bills/<int:bill_id>/discount', methods=['POST', 'DELETE'])
def manage_discount(bill_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)
        # Verify bill ownership
        cursor.execute("SELECT user_id FROM temporary_bills WHERE id = %s", (bill_id,))
        bill = cursor.fetchone()
        if not bill or bill['user_id'] != current_user.id:
            return jsonify({"error": "Not found or unauthorized"}), 404
        if request.method == 'POST':
            discount = request.json
            cursor.execute("""
                UPDATE temporary_bills
                SET bill_data = JSON_SET(
                    bill_data,
                    '$.discount',
                    JSON_OBJECT(
                        'type', %s,
                        'value', %s,
                        'applyToSubtotal', %s
                    )
                )
                WHERE id = %s
            """, (
                discount.get('type'),
                discount.get('value'),
                discount.get('applyToSubtotal', True),
                bill_id
            ))
            action = "added"
        else:  # DELETE
            cursor.execute("""
                UPDATE temporary_bills
                SET bill_data = JSON_REMOVE(bill_data, '$.discount')
                WHERE id = %s
            """, (bill_id,))
            action = "removed"
        conn.commit()
        return jsonify({"success": True, "action": action})
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def generate_bill_number(year):
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bill_sequence (year, next_number) VALUES (%s, 1) ON DUPLICATE KEY UPDATE next_number = last_insert_id(next_number + 1)", (year,))
        conn.commit()
        cursor.execute("SELECT last_insert_id()")
        next_number = cursor.fetchone()[0]
        return f"{year}-{next_number:06d}"
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error generating bill number: {str(e)}", file=sys.stderr)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@temp_bp.route('/', methods=['GET'])
def get_temporary_bills():
    pass
    return jsonify({})

# Create a new temporary bill
@temp_bp.route('/', methods=['POST']) # This route was correctly updated in a previous step.
def create_temporary_bill():
    """Create a new temporary bill"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Generate a temporary bill number
        bill_number = f"TEMP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

        # Create empty bill structure
        bill_data = {
            'items': [],
            'discount': None,
            'tax': None,
            'notes': '',
            'created_at': datetime.now().isoformat()
        }

        cursor.execute("""
            INSERT INTO temporary_bills
            (user_id, bill_number, bill_data, status, expires_at)
            VALUES (%s, %s, %s, 'draft', DATE_ADD(NOW(), INTERVAL 1 DAY))
        """, (
            current_user.id,
            bill_number,
            json.dumps(bill_data)
        ))

        bill_id = cursor.lastrowid
        conn.commit()

        return jsonify({
            "success": True,
            "bill_id": bill_id,
            "bill_number": bill_number,
            "redirect_url": f"/temp_bill/edit/{bill_id}"
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Get a specific temporary bill by ID
@temp_bp.route('/<int:bill_id>', methods=['GET']) # This route was correctly updated in a previous step.
def get_temporary_bill(bill_id):
    pass
    return jsonify({})

# Update a temporary bill
@temp_bp.route('/<int:bill_id>', methods=['PUT']) # This route was correctly updated in a previous step.
def update_temporary_bill(bill_id):
    pass
    return jsonify({})

# Delete a temporary bill
# Add an item to a temporary bill
@temp_bp.route('/add_item', methods=['POST'])
def add_item_to_temp_bill():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json
    bill_id = data.get('bill_id')
    name = data.get('name')
    price = data.get('price')
    quantity = data.get('quantity')

    if not all([bill_id, name, price, quantity]):
        # Note: This validation might need adjustment based on how you handle bill_id (create new vs add to existing)
        # If bill_id is optional for creating a new bill, the check should be different.
        return jsonify({"error": "Missing required fields"}), 400

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # Assuming temporary_bill_items table exists with columns: bill_id, name, price, quantity
        cursor.execute("""
            INSERT INTO temporary_bill_items (bill_id, name, price, quantity)
            VALUES (%s, %s, %s, %s)
        """, (bill_id, name, price, quantity))
        conn.commit()

        # You might want to return the updated bill data or the new item ID here
        # For simplicity, returning a success message for now.
        return jsonify({"message": "Item added successfully."}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Update an item in a temporary bill
def update_bill_item(bill_id, item_id):
# Export a temporary bill as PDF (using the template and bill data)

    pass
    return jsonify({})
@temp_bp.route('/add_item', methods=['POST'])
def add_bill_item():
    """
    Adds an item to an existing temporary bill or creates a new one.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    bill_id = data.get('bill_id')

    # Validate input
    if not product_id or quantity <= 0:
        return jsonify({"error": "Invalid input"}), 400

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get product details
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Create new bill if needed
        if bill_id is None or bill_id == 'new':
            cursor.execute("""
                INSERT INTO temporary_bills
                (user_id, bill_data, status, expires_at)
                VALUES (%s, %s, 'draft', NOW() + INTERVAL 1 DAY)
            """, (current_user.id, json.dumps({'items': []})))
            bill_id = cursor.lastrowid

        # Add item to bill
        new_item = {
            'product_id': product['id'],
            'product_name': product['description'],
            'unit_price': float(product['unit_price']),
            'quantity': int(quantity)
        }
        cursor.execute(
            "UPDATE temporary_bills SET bill_data = JSON_ARRAY_APPEND(bill_data, '$.items', %s) WHERE id = %s",
            (json.dumps(new_item), bill_id)
        )

        conn.commit()

        cursor.execute("SELECT * FROM temporary_bills WHERE id = %s", (bill_id,))
        updated_bill = cursor.fetchone()

        return jsonify({
            "success": True,
            "bill_id": bill_id,
            "bill_data": updated_bill['bill_data']
        })

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error adding item to bill: {e}", file=sys.stderr)
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@temp_bp.route('/<int:bill_id>/export/pdf', methods=['GET'])
def export_bill_pdf(bill_id):
    """
    Export a temporary bill as PDF
    """
    # TODO: Implement PDF export here
    return jsonify({"message": f"Export logic for bill {bill_id} coming soon"})


@temp_bp.route('/<int:bill_id>/items/<int:item_id>', methods=['DELETE']) # This route was correctly updated in a previous step.

def delete_bill_item(bill_id, item_id):
    pass
    return jsonify({})


# File Upload Handler
@temp_bp.route('/upload_asset', methods=['POST'])
def upload_asset():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure the upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        # TODO: Return the correct URL to access the file based on your server configuration
        return jsonify({'url': f'/uploads/{filename}'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@temp_bp.route('/templates', methods=['POST']) # This route was correctly updated in a previous step.
def create_template():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json
    name = data.get('name')
    html = data.get('html')
    thumbnail = data.get('thumbnail', None)
    user_id = current_user.id
    variables_json = json.dumps(data.get('variables', ["invoice_id", "date", "total"])) # Default variables

    if not name or not html:
        return jsonify({"error": "Name and HTML content are required"}), 400

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bill_templates (user_id, name, html, thumbnail, variables)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, html, thumbnail, variables_json))
        conn.commit()
        return jsonify({"message": "Template created successfully."}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Finalize a temporary bill (optional step to convert to a permanent record if needed)
@temp_bp.route('/<int:bill_id>/finalize', methods=['POST']) # This route was correctly updated in a previous step.
def finalize_temporary_bill(bill_id):
    pass
    return jsonify({})


# Edit an existing template
@temp_bp.route('/templates/<int:template_id>', methods=['PUT'])
def edit_template(template_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    data = request.json
    name = data.get('name')
    html = data.get('html')
    thumbnail = data.get('thumbnail', None)
    variables_json = json.dumps(data.get('variables', ["invoice_id", "date", "total"]))

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # Ensure the template belongs to the current user
        cursor.execute("SELECT user_id FROM bill_templates WHERE id = %s", (template_id,))
        template = cursor.fetchone()

        if not template:
            return jsonify({"error": "Template not found"}), 404
        if template[0] != current_user.id:
            return jsonify({"error": "Unauthorized to edit this template"}), 403

        cursor.execute("""
            UPDATE bill_templates SET name=%s, html=%s, thumbnail=%s, variables=%s
            WHERE id=%s
        """, (name, html, thumbnail, variables_json, template_id))
        conn.commit()
        return jsonify({"message": "Template updated successfully."})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Delete a template
@temp_bp.route('/templates/<int:template_id>', methods=['DELETE'])
def delete_template(template_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # Ensure the template belongs to the current user
        cursor.execute("SELECT user_id FROM bill_templates WHERE id = %s", (template_id,))
        template = cursor.fetchone()

        if not template:
            return jsonify({"error": "Template not found"}), 404
        if template[0] != current_user.id:
            return jsonify({"error": "Unauthorized to delete this template"}), 403

        cursor.execute("DELETE FROM bill_templates WHERE id=%s", (template_id,))
        conn.commit()
        return jsonify({"message": "Template deleted successfully."})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# Set a template as default
@temp_bp.route('/templates/<int:template_id>/set_default', methods=['PUT'])
def set_default(template_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401

    user_id = current_user.id
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # Ensure the template belongs to the current user
        cursor.execute("SELECT user_id FROM bill_templates WHERE id = %s", (template_id,))
        template = cursor.fetchone()

        if not template:
            return jsonify({"error": "Template not found"}), 404
        if template[0] != user_id:
            return jsonify({"error": "Unauthorized to set this template as default"}), 403


        cursor.execute("UPDATE bill_templates SET is_default=FALSE WHERE user_id=%s", (user_id,))
        cursor.execute("UPDATE bill_templates SET is_default=TRUE WHERE id=%s", (template_id,))
        conn.commit()
        return jsonify({"message": "Template set as default."})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify(error=str(e)), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()