from flask import Flask
from flask_login import LoginManager
from lib.database import Database
from lib.auth import auth_bp, setup_login_manager
from lib.products import products_bp
from lib.catalog import catalog_bp
import os
from temporarybill.temporary_bill_routes import temp_bp
from flask import render_template
from flask_wtf.csrf import CSRFProtect
from config import Config # Import your Config class

def create_app():
    app = Flask(__name__)
    
    # Set the secret key directly on the app IMMEDIATELY after creation
    print(f"Debug: Config.SECRET_KEY is: {Config.SECRET_KEY}")
    app.secret_key = Config.SECRET_KEY
    app.config.from_object(Config) # Load rest of config from Config object

    # Initialize CSRF protection
    csrf = CSRFProtect(app)
    # Setup login manager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    # Initialize database
    Database.initialize()
    
    # Register blueprints
    csrf.exempt(auth_bp)  # Exempt auth routes if needed
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(temp_bp, url_prefix='/api/temp_bills') # Register temporary bill blueprint
    app.add_url_rule('/static/uploads/<filename>', 'uploaded_file', build_only=True) # Define endpoint for uploaded files
    setup_login_manager(login_manager)

    # Basic route
    @app.route('/')
    def home():
        return render_template('landing.html')

    @app.route('/temporary_bill')
    def temporary_bill_page():
        return render_template('temporarybill/temporary_bill.html')

    # Route for creating a new temporary bill (frontend entry point)
    @app.route('/temp_bill/new')
    def new_temp_bill():
        return render_template('temporarybill/temporary_bill.html')

    # Route for editing a temporary bill
    @app.route('/temp_bill/edit/<int:bill_id>')
    def edit_temporary_bill_page(bill_id):
        return render_template('temporarybill/temporary_bill.html')

    return app
app = create_app()

# Configure static file serving for uploaded assets
app.static_folder = os.path.join(os.getcwd(), 'static')
app.static_url_path = '/static'

if __name__ == '__main__':
    app.run(debug=True)