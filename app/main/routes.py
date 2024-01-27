from flask import render_template
from app.main import bp

@bp.route("/home")
def home():
    return render_template("home.html") 

@bp.route("/reservations")
def reservations():
    return render_template("reservations.html") 