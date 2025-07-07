import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(

)
cursor = conn.cursor()

# Create Database
cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_db")
cursor.execute("USE inventory_db")

# Create Users table FIRST (since other tables reference it)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role ENUM('admin', 'manager', 'staff') DEFAULT 'staff',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Create Categories Table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL
    )
""")

# Create Products Table (Updated)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category_id INT,
        brand VARCHAR(100),
        description TEXT,
        unit_price DECIMAL(10,2),
        quantity_in_stock INT,
        min_stock_level INT,
        is_deleted TINYINT(1) DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )
""")

# Create Specifications Tables
spec_tables = [
    ("switches", "amp_rating DECIMAL(5,2), module_type VARCHAR(50), color VARCHAR(50)"),
    ("tubelights", "wattage DECIMAL(5,2), color_temperature VARCHAR(50)"),
    ("pipes", "material VARCHAR(50), length DECIMAL(6,2), diameter DECIMAL(5,2)"),
    ("wires", "voltage_rating DECIMAL(6,2), insulation_type VARCHAR(50)"),
    ("panels", "voltage_rating DECIMAL(6,2), material VARCHAR(50)"),
    ("led", "wattage DECIMAL(5,2), color_temperature VARCHAR(50)")
]

for category, columns in spec_tables:
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {category}_specifications (
            id INT PRIMARY KEY,
            {columns},
            FOREIGN KEY (id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

# Price history table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_id INT NOT NULL,
        old_price DECIMAL(10,2) NOT NULL,
        new_price DECIMAL(10,2) NOT NULL,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        changed_by INT,
        source VARCHAR(255),
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (changed_by) REFERENCES users(id)
    )
""")

# Add new columns using ALTER TABLE with checks
try:
    cursor.execute("ALTER TABLE products ADD COLUMN last_catalog_update DATE AFTER is_deleted")
except mysql.connector.Error as err:
    if err.errno != 1060: # 1060 is "Duplicate column name"
        print(f"✗ Failed to add 'last_catalog_update' column: {err}")

try:
    cursor.execute("ALTER TABLE price_history ADD COLUMN is_catalog_update BOOLEAN DEFAULT FALSE AFTER source")
    print("✓ Added 'is_catalog_update' column to 'price_history' table")
except mysql.connector.Error as err:
    if err.errno != 1060:
        print(f"✗ Failed to add 'is_catalog_update' column: {err}")


# Catalog processing logs
cursor.execute("""
    CREATE TABLE IF NOT EXISTS catalog_processing_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_by INT,
        total_changes INT,
        auto_approved INT,
        changes_json JSON,
        FOREIGN KEY (processed_by) REFERENCES users(id)
    )
""")

# Add changes_json column using ALTER TABLE with checks
cursor.execute("""
    ALTER TABLE catalog_processing_logs ADD COLUMN changes_json JSON AFTER auto_approved
""")

# Insert predefined categories
cursor.execute("""
    INSERT IGNORE INTO categories (name)
    VALUES
        ('switches'),
        ('tubelights'),
        ('pipes'),
        ('wires'),
        ('panels'),
        ('LED')
""")

# Create initial admin user
admin_username = "admin"
admin_password = "admin123"  # Change this in production!
hashed_password = generate_password_hash(admin_password)

try:
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'admin')
        ON DUPLICATE KEY UPDATE password_hash=%s, role='admin'
    """, (admin_username, hashed_password, hashed_password))
    conn.commit()
    print(f"✓ Admin user created: {admin_username}")
except Exception as e:
    print(f"✗ Error creating admin user: {str(e)}")

admin_username = "admin"  # Change if needed
admin_password = "admin123"  # CHANGE THIS IN PRODUCTION
hashed_password = generate_password_hash(admin_password)

try:
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'admin')
        ON DUPLICATE KEY UPDATE password_hash=%s
    """, (admin_username, hashed_password, hashed_password))
    conn.commit()
    print(f"Created admin user: {admin_username}")
except Exception as e:
    print(f"Error creating admin user: {str(e)}")


conn.commit()
cursor.close()
conn.close()
