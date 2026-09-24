from flask import Blueprint, current_app, jsonify

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def index():
    return jsonify(
        {
            "service": current_app.config["SERVICE_NAME"],
            "status": "available",
            "documentation": {
                "liveness": "/health/live",
                "readiness": "/health/ready",
                "system": "/health/system",
            },
        }
    )
