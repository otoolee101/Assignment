from flask import flash, redirect, render_template, request, url_for
from flask_login import login_required
from app.main import bp
from app.extensions import db
from app.models.models import reserve

@bp.route("/reserve_parking", methods=["GET", "POST"])
@login_required
def reserve_parking():
    if request.form:
        reservation = reserve(username=request.form.get("username"), registration=request.form.get("registration"), date=request.form.get("date"))
        try:
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation created successfully")
            return redirect(url_for("main.reserve_parking"))
        except: 
            flash("Reservation failed to create. Please contact system administration.")
            return render_template("main/reserve_parking.html")
    return render_template("reserve_parking.html") 

@bp.route("/reservations")
@login_required
def reservations():
    reservation = reserve.query.all()
    return render_template("reservations.html", reservation=reservation) 

