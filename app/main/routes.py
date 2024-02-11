from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.main import bp
from app.extensions import db
from app.models.models import reserve
   
@bp.route("/reserve_parking", methods=["GET", "POST"])
@login_required
def reserve_parking():
    if current_user.authorised =='Y':
        if request.form:
            current_app.logger.info('Username: %s accessed reserve_parking', current_user.username)
            reservation = reserve(username=request.form.get("username"), registration=request.form.get("registration"), date=request.form.get("date"))
            try:
                db.session.add(reservation)
                db.session.commit()
                current_app.logger.info('Username: %s created a new bookings in reserve_parking', current_user.username)
                flash("Reservation created successfully")
                return redirect(url_for("main.reserve_parking"))
            except: 
                flash("Reservation failed to create. Please contact system administration.")
                current_app.logger.info('Username: %s had a failure when creating a booking for reserve_parking', current_user.username)
                return render_template("main/reserve_parking.html")
        return render_template("reserve_parking.html") 
    else: 
        current_app.logger.warning('Username: %s attempted to access reserve_parking when they are not authorised', current_user.username)
        return render_template("unauthorised.html") 
        
@bp.route("/reservations")
@login_required
def reservations():
    if current_user.authorised =='Y':
        if current_user.role =='admin':
            reservation = reserve.query.all()
            current_app.logger.info('Username: %s accessed reservations', current_user.username)
        else:
            reservation = reserve.query.filter_by(username = current_user.username).all()
            current_app.logger.info('Username: %s accessed reservations', current_user.username)
        return render_template("reservations.html", reservation=reservation) 
    else: 
        current_app.logger.warning('Username: %s attempted to access reservations when they are not authorised', current_user.username)
        return render_template("unauthorised.html") 
    
@bp.route("/edit_reservations/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_reservations(id):
    """Gets the current username of the person logged in 
    and the username of the reservation and if they dont match it will not allow updates but still allows admin updates."""
    edit = reserve.query.get_or_404(id)
    if current_user.authorised == 'Y' and (current_user.username == edit.username or current_user.role =='admin'):
        if request.method == "POST":
            current_app.logger.info('Username: %s accessed edit reservation', current_user.username)
            edit.username = request.form['username']
            edit.registration = request.form['registration']
            edit.date = request.form['date']
            try:
                db.session.commit()
                current_app.logger.info('Username: %s edited a reservation %s', current_user.username, edit.id)
                flash("Reservation updated successfully")
                return redirect(url_for("main.reservations"))
            except:
                flash("Reservation failed to update")
                current_app.logger.warning('Username: %s failed to edit a reservation %s', current_user.username, edit.id)
                return render_template("reservations.html", edit=edit)        
        else:
            current_app.logger.warning('Username: %s failed to access reservations', current_user.username)
            return render_template("edit_reservation.html", edit=edit)
    else: 
        current_app.logger.critical('Username: %s attempted to edit reservations %s', current_user.username, edit.id)
        return render_template("unauthorised.html")