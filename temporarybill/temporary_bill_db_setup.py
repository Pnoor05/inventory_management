from lib.database import Database
import sys

def setup_bill_templates_table():
    """Sets up the bill_templates table in the database."""
    conn = None
    cursor = None
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()

        # SQL statement to create the bill_templates table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS bill_templates (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            html MEDIUMTEXT NOT NULL,
            thumbnail VARCHAR(255),
            is_default BOOLEAN DEFAULT FALSE,
            variables JSON DEFAULT '["invoice_id", "date", "total"]',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """

        cursor.execute(create_table_sql)
        conn.commit()
        print("bill_templates table created or already exists.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error setting up bill_templates table: {str(e)}", file=sys.stderr)

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    setup_bill_templates_table()