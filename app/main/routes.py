import datetime
from operator import or_
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from app.main import bp
from app.extensions import db
from app.models.models import reserve
   
@bp.route("/reserve_parking", methods=["GET", "POST"])
@login_required
def reserve_parking():
    if current_user.authorised == 'Y':
        if request.method == "POST":
            current_app.logger.info('Username: %s accessed reserve_parking', current_user.username)
            date = request.form.get("date")
            available_spaces_count = available_spaces(date)
            if available_spaces_count > 0:
                reservation = reserve(username=request.form.get("username"),registration=request.form.get("registration"), date=date)
                try:
                    db.session.add(reservation)
                    db.session.commit()
                    current_app.logger.info('Username: %s created a new booking in reserve_parking', current_user.username)
                    flash("Reservation created successfully.")
                    return redirect(url_for("main.reserve_parking"))
                except:
                    flash("Reservation failed to create. Please contact system administration.")
                    current_app.logger.exception('Username: %s had a failure when creating a booking for reserve_parking: %s', current_user.username)
                    return render_template("main/reserve_parking.html")
            else:
                flash("All parking spaces for this date are booked. Please select another date.")
        return render_template("reserve_parking.html")
    else:
        current_app.logger.warning('Username: %s attempted to access reserve_parking when they are not authorised', current_user.username)
        flash("You are not authorised to access this page")
        return redirect(url_for("user.login"))

#Check how many spaces are available that are not cancelled. With a maximum of 5 spaces
def available_spaces(date):
    reserved_spaces_count = reserve.query.filter(reserve.date==date, reserve.cancelled == 'N').count()
    available_spaces_count = 5 - reserved_spaces_count
    return available_spaces_count

@bp.route("/reservations")
@login_required
def reservations():
    if current_user.authorised =='Y':
        if current_user.role =='admin':
            active_reservations = reserve.query.filter(reserve.cancelled == 'N', reserve.date >= func.current_date()).all()
            inactive_reservations = reserve.query.filter(or_(reserve.cancelled == 'Y', reserve.date < func.current_date())).all()
            current_app.logger.info('Username: %s accessed reservations', current_user.username)
        else:
            active_reservations = reserve.query.filter(reserve.cancelled == 'N', reserve.date >= func.current_date(), reserve.username == current_user.username).all()
            inactive_reservations = reserve.query.filter(or_(reserve.cancelled == 'Y', reserve.date < func.current_date()), reserve.username == current_user.username).all()
            current_app.logger.info('Username: %s accessed reservations', current_user.username)
        return render_template("reservations.html", active_reservations=active_reservations, inactive_reservations=inactive_reservations) 
    else: 
        current_app.logger.warning('Username: %s attempted to access reservations when they are not authorised', current_user.username)
        flash("You are not authorised to access this page")
        return redirect(url_for("user.login"))

    
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
                return redirect(url_for('main.reservations'))
            except:
                flash("Reservation failed to update")
                current_app.logger.warning('Username: %s failed to edit a reservation %s', current_user.username, edit.id)
                return redirect(url_for('main.reservations', edit=edit))      
        else:
            current_app.logger.warning('Username: %s failed to access reservations', current_user.username)
            return render_template("edit_reservation.html", edit=edit)
    else: 
        current_app.logger.critical('Username: %s attempted to edit reservations %s', current_user.username, edit.id)
        flash("You are not authorised to access this page")
        return redirect(url_for("main.reservations"))
    
@bp.route("/cancel_reservation/", methods=['GET', 'POST'])
@login_required
def cancel_reservation():
    id = request.form.get('id')
    reservation = reserve.query.get(id) 
    if current_user.authorised == 'Y' and (current_user.username == reservation.username or current_user.role =='admin'):
        if request.method == 'POST':
            reservation.cancelled = 'Y'
            try:
                db.session.commit() 
                current_app.logger.info('Username: %s cancelled reservation: %s', current_user.username, reservation.id)
                flash("Reservation cancelled successfully.")
                return redirect(url_for('main.reservations'))
            except:
                flash("Cancel reservation failed.")
                current_app.logger.info('Username: %s failed to cancelled reservation: %s', current_user.username, reservation.id)
                return redirect(url_for('main.reservations'))
        else:
            flash("Cancel reservation failed.")
            current_app.logger.info('Username: %s failed to cancelled reservation: %s', current_user.username, reservation.id)
            return redirect(url_for('main.reservations'))
    else: 
        current_app.logger.critical('Username: %s attempted to cancel reservations %s', current_user.username, reservation.id)
        flash("You are not authorised to access this page")
        return render_template("reservations.html")