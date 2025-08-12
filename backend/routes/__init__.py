from controllers.user_controller import bp as users_bp
from controllers.project_controller import bp as projects_bp
from controllers.document_controller import bp as documents_bp
from controllers.person_controller import bp as people_bp
from controllers.decision_controller import bp as decisions_bp
from controllers.chunk_controller import bp as chunks_bp


def register_routes(app):
    app.register_blueprint(users_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(people_bp)
    app.register_blueprint(decisions_bp)
    app.register_blueprint(chunks_bp)
