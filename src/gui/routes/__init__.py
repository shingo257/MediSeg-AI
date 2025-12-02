"""
Flask Blueprintの登録
"""

from flask import Blueprint

from src.gui.routes.health import health_bp
from src.gui.routes.system import system_bp
from src.gui.routes.datasets import datasets_bp
from src.gui.routes.segmentation import segmentation_bp
from src.gui.routes.visualization import visualization_bp


def register_blueprints(app):
    """Blueprintをアプリケーションに登録"""
    app.register_blueprint(health_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(segmentation_bp)
    app.register_blueprint(visualization_bp)

