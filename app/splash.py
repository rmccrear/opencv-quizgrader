from flask import render_template

def setup_splash(app):
    @app.route("/")
    def splash_page():
        return render_template("splash.html")