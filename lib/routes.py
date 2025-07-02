'''
# lib/routes.py
"""
Central route definitions that don't fit in blueprints
"""

from flask import render_template
from lib.database import Database

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('error.html', error="Internal server error"), 500
        '''

# lib/routes.py
"""
Central route definitions that don't fit in blueprints
"""

from flask import render_template
from lib.database import Database

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return render_template('error.html', error="Internal server error"), 500