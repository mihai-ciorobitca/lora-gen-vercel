from flask import Flask, render_template, redirect, url_for, request
from extensions import cache
from blueprints.auth.routes import auth_bp
from blueprints.dashboard.routes import dashboard_bp
from blueprints.admin.routes import admin_bp
from os import getenv


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    app.secret_key = getenv("FLASK_KEY")

    cache.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def check_for_maintenance():
        MAINTENANCE = getenv("MAINTENANCE")
        if MAINTENANCE == "TRUE":
            allowed_prefixes = ["/admin", "/auth/login", "/health", "/static"]
            if not any(request.path.startswith(p) for p in allowed_prefixes):
                return render_template("maintenance.html"), 503

    @app.route("/")
    @cache.cached(timeout=3600)
    def index():
        return redirect(url_for("dashboard.dashboard_get"))

    @app.route("/pricing")
    @cache.cached(timeout=3600)
    def pricing():
        return render_template("pricing.html")

    @app.route("/success")
    def success():
        return render_template("success.html")

    @app.errorhandler(404)
    @cache.cached(timeout=3600)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    @cache.cached(timeout=3600)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @app.route("/faq")
    @cache.cached(timeout=3600)
    def faq():
        return render_template("faq.html")

    @app.route("/health")
    @cache.cached(timeout=0)
    def health_check():
        return "OK", 200

    return app


app = create_app()

app.run(debug=True)
