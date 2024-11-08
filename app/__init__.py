# __init__.py
import boto3
from flask import Flask
from flask_login import LoginManager

from app.utils.template_filters import replace_newline

login_manager = LoginManager()
login_manager.login_view = "app.view"
login_manager.login_message = "Please log in"


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "mysite"
    app.add_template_filter(replace_newline)

    # Initiate DynamoDB client
    db = boto3.client('dynamodb', region_name="us-east-1")

    # Add DDB to application context
    app.dynamodb = db

    from app.views.views import bp
    app.register_blueprint(bp)
    login_manager.init_app(app)

    return app
