from functools import wraps
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.admin import bp
from app.models.models import User, reserve
from app.extensions import db
from app.main.routes import check_authorisation

#Function checks if user is of the role admin when attempting to access centain functions. 
#If they are not it will return them to the reserve_parking page and put a line in the log.
def check_is_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role == 'admin':
            return func(*args, **kwargs)
        else:
            current_app.logger.critical('Username: %s accessed attempted to access %s', current_user.username,func.__name__)
            flash("You are not authorised to access this page")
            return redirect(url_for("main.reserve_parking"))
    return decorated_function
    
#Function to return all user account when you are loggined in as a admin user.
@bp.route("/admin/")
@login_required
@check_authorisation
@check_is_admin
def admin():
    try: 
        admin= User.query.all()
        current_app.logger.info('Username: %s accessed admin', current_user.username)
        return render_template('admin.html',admin=admin)
    except Exception as e: 
        flash("An error occurred retrieving users.")
        current_app.logger.exception('Error during retrieving all users: %s', str(e))
        return redirect(url_for('main.reserve_parking'))

    
#Function to be able to edit a username or role
@bp.route("/edit_user/<int:id>", methods=['GET','POST'])
@login_required
@check_authorisation
@check_is_admin
def edit_user(id):
    admin = User.query.get_or_404(id) 

    if request.method == "POST":
        current_app.logger.info('Username: %s accessed edit_user', current_user.username)
        admin.username = request.form['username']
        admin.registration = request.form['registration']
        admin.role = request.form['role']
        admin.authorised = request.form['authorised']

        #Save update to database
        try:
            db.session.commit()
            current_app.logger.info('Username: %s updated user account %s', current_user.username, admin.username)
            flash("User updated successfully")
            return redirect(url_for("admin.admin"))
        except Exception as e:
            current_app.logger.exception(e)
            flash("User failed to update")
            current_app.logger.warning('Username: %s failed to update user account %s', current_user.username, admin.username)
            return render_template("edit_user.html", admin=admin)
            
    else:
        return render_template("edit_user.html", admin=admin)

#Function to delete  users.
@bp.route("/delete_user/", methods=['GET', 'POST'])
@login_required
@check_authorisation
@check_is_admin
def delete_user():
    id = request.form.get("id")
    delete_user = User.query.filter_by(id=id).first()

    try:
        db.session.delete(delete_user)
        current_app.logger.warning('Username: %s deleted %s account', current_user.username, delete_user.username)
        db.session.commit()
        flash("User was deleted successfully.")
        return redirect(url_for("admin.admin"))
    except Exception as e:
        flash("User failed to delete.")
        current_app.logger.warning('Username: %s failed to deleted an account', current_user.username)
        return render_template("admin.html")

#function to delete tickets, only visiable for admin users
@bp.route("/delete_reservation/", methods=['GET', 'POST'])
@login_required
@check_authorisation
@check_is_admin
def delete_reservation():
    id = request.form.get("id")
    delete_reservation = reserve.query.filter_by(id=id).first()

    try:
        db.session.delete(delete_reservation)
        current_app.logger.warning('Username: %s deleted reservation: %s ', current_user.username, delete_reservation.id)
        db.session.commit()
        flash("Reservation was deleted successfully.")
        return redirect(url_for("main.reservations"))
    except Exception as e:
        flash("Reservation failed to delete")
        current_app.logger.warning('Username: %s failed to deleted reservation: %s ', current_user.username, delete_reservation.id)
        return redirect(url_for("main.reservations"))

#Function to return logged messages
@bp.route('/logging_messages')
@login_required
@check_authorisation
@check_is_admin
def logging_messages():
        log_file_path = 'app.log'
        log_content = read_log_file(log_file_path)

        return render_template('logging_messages.html', log_content=log_content)
   
def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            log_content = file.read()
        return log_content
    
    except FileNotFoundError:
        return "Log file not found"