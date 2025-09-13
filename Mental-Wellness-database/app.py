from flask import Flask
from flask_cors import CORS
from routes.personality_routes import personality_bp
from routes.chat_routes import chat_bp
from routes.auth_routes import auth_bp # Import the new auth blueprint
from utils import db 

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api") # Register auth routes
app.register_blueprint(personality_bp, url_prefix="/api/personality")
app.register_blueprint(chat_bp, url_prefix="/api") 

# Root health check
@app.route("/")
def home():
    return {"message": "Mental Wellness Backend is running 🚀"}

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)