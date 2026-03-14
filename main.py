from flask import Flask, redirect, url_for

from database.init import init_app as init_database
from courses.route import courses_bp
from departments.route import departments_bp
from schools.route import schools_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    # app.config["DATABASE"] = "course.db"

    init_database(app)
    app.register_blueprint(schools_bp, url_prefix="/schools")
    app.register_blueprint(departments_bp, url_prefix="/departments")
    app.register_blueprint(courses_bp, url_prefix="/courses")

    @app.route("/")
    def index():
        return redirect(url_for("schools.index"))

    return app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True)