# backend/app.py
import os
import sys
import logging
import codecs
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from flask_socketio import SocketIO
from routes.friends_routes import friends_bp
from routes.home_routes import home_bp
from routes.task_routes import task_bp
# Load environment variables first
load_dotenv()

class MentalWellnessApp:
    def __init__(self):
        self.app = Flask(__name__)
        # Add SocketIO initialization for real-time features
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        self.initialization_status = {
            'mongodb': False,
            'auth_routes': False,
            'chat_routes': False,
            'community_routes': False,
            'safety_routes': False
        }
        self.setup_logging()
        self.setup_import_paths()
        self.setup_cors()
        self.setup_database()
        self.register_blueprints()
        self.setup_health_routes()
        self.setup_error_handlers()
        self.setup_static_file_serving()


    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def setup_import_paths(self):
        """Set up Python import paths"""
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    def setup_cors(self):
        """Enable CORS for the app"""
        CORS(self.app)

    def setup_database(self):
        """Initialize MongoDB connection"""
        try:
            self.logger.info("🔄 Initializing MongoDB connection...")
            from utils.db import get_db
            get_db() # This will run the connection check
            self.initialization_status['mongodb'] = True
            self.logger.info("✅ MongoDB initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ MongoDB initialization failed: {e}")

    def register_blueprints(self):
        """Register all Flask blueprints"""
        # Auth routes (with new search endpoint)
        try:
            from routes.auth_routes import auth_bp
            self.app.register_blueprint(auth_bp, url_prefix="/api")
            self.initialization_status['auth_routes'] = True
            self.logger.info("✅ Auth routes registered")
        except Exception as e:
            self.logger.error(f"❌ Auth routes registration failed: {e}")

        # Chat routes
        try:
            from routes.chat_routes import chat_bp
            self.app.register_blueprint(chat_bp, url_prefix="/api")
            self.initialization_status['chat_routes'] = True
            self.logger.info("✅ Chat routes registered")
        except Exception as e:
            self.logger.error(f"❌ Chat routes registration failed: {e}")

        # Community routes
        try:
            from routes.community_routes import community_bp
            # Pass socketio instance to the blueprint
            community_bp.socketio = self.socketio
            self.app.register_blueprint(community_bp, url_prefix="/api/community")
            self.initialization_status['community_routes'] = True
            self.logger.info("✅ Community routes registered")
        except Exception as e:
            self.logger.error(f"❌ Community routes registration failed: {e}")

        # Safety routes
        try:
            from routes.safety_routes import safety_bp
            self.app.register_blueprint(safety_bp, url_prefix="/api/safety")
            self.initialization_status['safety_routes'] = True
            self.logger.info("✅ Safety routes registered")
        except Exception as e:
            self.logger.error(f"❌ Safety routes registration failed: {e}")

        # Register the new home routes
        
        try:
            self.app.register_blueprint(home_bp, url_prefix="/api")
            self.initialization_status['home_routes'] = True
            self.logger.info("✅ Home routes registered")
        except Exception as e:
            self.logger.error(f"❌ Home routes registration failed: {e}")

        # Register the task routes
        try:
            self.app.register_blueprint(task_bp, url_prefix="/api")
            self.initialization_status['task_routes'] = True
            self.logger.info("✅ Task routes registered")
        except Exception as e:
            self.logger.error(f"❌ Task routes registration failed: {e}")

        # Register the friends routes
        try:
            self.app.register_blueprint(friends_bp, url_prefix="/api/friends")
            self.initialization_status['friends_routes'] = True
            self.logger.info("✅ Friends routes registered")
        except Exception as e:
            self.logger.error(f"❌ Friends routes registration failed: {e}")

    def setup_health_routes(self):
        @self.app.route("/")
        def home():
            return jsonify({
                "message": "Mental Wellness Backend is running 🚀",
                "status": "healthy",
                "initialization": self.initialization_status
            })

    def setup_error_handlers(self):
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({"success": False, "error": "Endpoint not found"}), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({"success": False, "error": "Internal server error"}), 500

    def setup_static_file_serving(self):
        @self.app.route('/uploads/<filename>')
        def uploaded_file(filename):
            return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'), filename)

    def run(self):
        """Run the Flask-SocketIO application"""
        self.logger.info("🚀 Starting Mental Wellness Backend with real-time features...")
        self.logger.info("🌐 Server starting on http://127.0.0.1:5000")
        # Use socketio.run() to enable WebSocket support
        self.socketio.run(self.app, debug=True, host="127.0.0.1", port=5000, use_reloader=False)

# Create and run the application
app_instance = MentalWellnessApp()
app = app_instance.app
socketio = app_instance.socketio # Expose for potential other uses

if __name__ == "__main__":
    app_instance.run()