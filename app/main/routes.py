from functools import wraps
from operator import or_
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from app.main import bp
from app.extensions import db
from app.models.models import reserve
from datetime import datetime

#Function checks if user is authorised when attempting to access each function. 
#If they are not it will return them to login page and put a line in the log. 
def check_authorisation(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.authorised == 'Y':
            return func(*args, **kwargs)
        else:
            current_app.logger.warning('Username: %s attempted to access %s when they are not authorised', current_user.username, func.__name__)
            flash("You are not authorised to access this page")
            return redirect(url_for("user.login"))
    return decorated_function

#Function to reserve a car parking space 
@bp.route("/reserve_parking", methods=["GET", "POST"])
@login_required
@check_authorisation
def reserve_parking():
    if request.method == "POST":
        #Section checks date entered in the form then calls on available_spaces_count to check there are spaces available to book
        current_app.logger.info('Username: %s accessed reserve_parking', current_user.username)
        date_str = request.form.get("date")
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        available_spaces_count = available_spaces(date)

        #If there are more than 0 spaces available then save the reservation to the database. 
        if available_spaces_count > 0:
            reservation = reserve(username=request.form.get("username"),registration=request.form.get("registration"), date=date)

            #Save to the database
            try:
                db.session.add(reservation)
                db.session.commit()
                current_app.logger.info('Username: %s created a new booking in reserve_parking', current_user.username)
                flash("Reservation created successfully.")
                return redirect(url_for("main.reserve_parking"))
            except Exception as e:
                flash("Reservation failed to create. Please contact system administration.")
                current_app.logger.exception('Username: %s had a failure when creating a booking for reserve_parking: %s', current_user.username)
                return render_template("main/reserve_parking.html")
            
        #Else there is no spaces left, do not save to database. 
        else:
            flash("All parking spaces for this date are booked. Please select another date.")
            
    return render_template("reserve_parking.html")
        
#Check how many spaces are available that are not cancelled. With a maximum of 5 spaces
def available_spaces(date):
    reserved_spaces_count = reserve.query.filter(reserve.date==date, reserve.cancelled == 'N').count()
    available_spaces_count = 5 - reserved_spaces_count
    return available_spaces_count

#Retrieve reservations into table. There are two tables active and inactive. Active shows all reserversation equal or greater than todays date. 
#Inactive table shows any cancelled reservations or reservations before todays date. 
@bp.route("/reservations")
@login_required
@check_authorisation
def reservations():
    try:
        #If the user is admin show all reservation in the table. 
        if current_user.role =='admin':
            active_reservations = reserve.query.filter(reserve.cancelled == 'N', reserve.date >= func.current_date()).all()
            inactive_reservations = reserve.query.filter(or_(reserve.cancelled == 'Y', reserve.date < func.current_date())).all()

        else:
        #Else show reservations that only the user logged in has created. 
            active_reservations = reserve.query.filter(reserve.cancelled == 'N', reserve.date >= func.current_date(), reserve.username == current_user.username).all()
            inactive_reservations = reserve.query.filter(or_(reserve.cancelled == 'Y',reserve.date < func.current_date()), reserve.username == current_user.username).all()
            
        current_app.logger.info('Username: %s accessed reservations', current_user.username)

        return render_template("reservations.html", active_reservations=active_reservations, inactive_reservations=inactive_reservations) 
    
    except Exception as e: 
        flash("An error occurred retrieving reservations. Please try again.")
        current_app.logger.exception('Error during retrieving reservations: %s', str(e))
        return redirect(url_for('main.reserve_parking'))
    
#Function to edit the reservation created. 
@bp.route("/edit_reservations/<int:id>", methods=['POST', 'GET'])
@login_required
@check_authorisation
def edit_reservations(id):
    edit = reserve.query.get_or_404(id)
    #Checks the current user logged is matches the username of the person who created the reservation or admin. 
    #If it does not match it will not allow an update.
    if current_user.username == edit.username or current_user.role =='admin':
        if request.method == "POST":
            current_app.logger.info('Username: %s accessed edit reservation', current_user.username)
            edit.username = request.form['username']
            edit.registration = request.form['registration']
            date_str = request.form['date']
            edit.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            #Save update to database
            try:
                db.session.commit()
                current_app.logger.info('Username: %s edited a reservation %s', current_user.username, edit.id)
                flash("Reservation updated successfully")
                return redirect(url_for('main.reservations'))
            except Exception as e:
                flash("Reservation failed to update")
                current_app.logger.warning('Username: %s failed to edit a reservation %s', current_user.username, edit.id)
                return redirect(url_for('main.reservations', edit=edit))  
                
        else:
            current_app.logger.warning('Username: %s failed to access reservations', current_user.username)
            return render_template("edit_reservation.html", edit=edit)
    
    #User not owner of reservation or admin so do not update 
    else: 
        current_app.logger.critical('Username: %s attempted to edit reservations %s', current_user.username, edit.id)
        flash("You are not authorised to access this page")
        return redirect(url_for("main.reservations"))
    

#Cancel the reservation the user used.   
@bp.route("/cancel_reservation/", methods=['GET', 'POST'])
@login_required
@check_authorisation
def cancel_reservation():
    id = request.form.get('id')
    reservation = reserve.query.get(id) 
    #Checks the current user logged is matches the username of the person who created the reservation or admin. 
    #If it does not match it will not allow cancel.
    if current_user.username == reservation.username or current_user.role =='admin':

        if request.method == 'POST':
            #Set cancelled to Y in database 
            reservation.cancelled = 'Y'

            #Save to database
            try:
                db.session.commit() 
                current_app.logger.info('Username: %s cancelled reservation: %s', current_user.username, reservation.id)
                flash("Reservation cancelled successfully.")
                return redirect(url_for('main.reservations'))
            except Exception as e:
                flash("Cancel reservation failed.")
                current_app.logger.info('Username: %s failed to cancelled reservation: %s', current_user.username, reservation.id)
                return redirect(url_for('main.reservations'))
        
        else:
            flash("Cancel reservation failed.")
            current_app.logger.info('Username: %s failed to cancelled reservation: %s', current_user.username, reservation.id)
            return redirect(url_for('main.reservations'))
        
    #User not owner of reservation or admin so do not cancel 
    else: 
        current_app.logger.critical('Username: %s attempted to cancel reservations %s', current_user.username, reservation.id)
        flash("You are not authorised to access this page")
        return render_template("reservations.html")