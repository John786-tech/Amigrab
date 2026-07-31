"""
AmiGrab - Campus Canteen Delivery Application
Enhanced Backend with Modular Architecture

This is the updated main application file that uses:
- Blueprint-based routing (auth, main, delivery)
- Configuration management (config.py)
- Database models (models.py)
- Utility functions (utils/)

SETUP INSTRUCTIONS:
1. Install dependencies: pip install -r requirements.txt
2. Create .env file with required variables
3. Run: python app.py
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for, session
from flask_migrate import Migrate
from config import config
from models import db
from utils.helpers import setup_logger, get_current_user

# ============== APPLICATION FACTORY ==============
def create_app(config_name='development'):
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Setup logging
    logger = setup_logger(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.delivery import delivery_bp
    
    app.register_blueprint(auth_bp, url_prefix='')
    app.register_blueprint(main_bp, url_prefix='')
    app.register_blueprint(delivery_bp, url_prefix='')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"500 Error: {error}")
        return render_template('500.html'), 500
    
    # Context processor for templates
    @app.context_processor
    def inject_user():
        return {'current_user': get_current_user()}
    
    # Static file serving
    @app.route('/sw.js')
    def service_worker():
        return app.send_static_file('sw.js')
    
    return app


# ============== DATABASE INITIALIZATION ==============
def init_database(app):
    """Initialize database and seed data"""
    with app.app_context():
        # Create upload folder
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Create all tables
        db.create_all()
        
        # Seed sample data if needed
        from models import Canteen
        if not Canteen.query.first():
            from models import seed_data
            seed_data()
            print("✓ Database seeded with sample data")
        else:
            print("✓ Database already initialized")


# ============== MAIN ENTRY POINT ==============
if __name__ == '__main__':
    # Determine environment
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create app
    app = create_app(env)
    
    # Initialize database
    init_database(app)
    
    # Run development server
    debug_mode = env == 'development'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║    🍔 AmiGrab - Campus Canteen App      ║
    ║           Enhanced Version 2.0          ║
    ╚══════════════════════════════════════════╝
    
    Environment: {env.upper()}
    Debug Mode: {debug_mode}
    Server: http://{host}:{port}
    
    ✓ Authentication with role-based access
    ✓ Gmail required for delivery partners
    ✓ Modern responsive UI
    ✓ Modular architecture
    ✓ Database optimization
    
    Press CTRL+C to stop the server.
    """)
    
    app.run(
        debug=debug_mode,
        host=host,
        port=port,
        use_reloader=debug_mode
    )
