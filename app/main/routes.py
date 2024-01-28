from flask import render_template
from app.main import bp

@bp.route("/reserve_parking")
def home():
    return render_template("reserve_parking.html") 

@bp.route("/reservations")
def reservations():
    return render_template("reservations.html") 