from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
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
    if current_user.role =='admin':
        reservation = reserve.query.all()
    else:
        reservation = reserve.query.filter_by(username = current_user.username).all()
    return render_template("reservations.html", reservation=reservation) 

@bp.route("/edit_reservations/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_reservations(id):
    edit = reserve.query.get_or_404(id)
    if request.method == "POST":
        edit.username = request.form['username']
        edit.registration = request.form['registration']
        edit.date = request.form['date']
        try:
            db.session.commit()
            flash("Ticket updated successfully")
            return redirect(url_for("main.reservations"))
        except:
            flash("Ticket failed to update")
            return render_template("reservations.html", edit=edit)        
    else:
        return render_template("edit_reservation.html", edit=edit)