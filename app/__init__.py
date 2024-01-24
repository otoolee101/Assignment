from flask import Flask
from flask_login import LoginManager

from app.extensions import db

from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    #login_manager.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    #from app.user import bp as user_bp
    #app.register_blueprint(user_bp)
    #from app.admin import bp as admin_bp
    #app.register_blueprint(admin_bp)

    #from app.models.models import User
    #@login_manager.user_loader
    #def load_user(user_id):
     #   return User.query.get(int(user_id))

    return app

#login_manager = LoginManager()
#login_manager.login_view = 'user.login'