from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.admin import bp
from app.models.models import User, reserve
from app.extensions import db
    
"""Function to return all user account when you are loggined in as a admin user."""
@bp.route("/admin/")
@login_required
def admin():
    if current_user.role == 'admin':
        admin= User.query.all()
        current_app.logger.info('Username: %s accessed admin', current_user.username)
        return render_template('admin.html',admin=admin)
    else:
        current_app.logger.critical('Username: %s accessed attempted to access admin', current_user.username)
        return render_template("unauthorised.html")
    
"""Function to be able to edit a username or role"""
@bp.route("/edit_user/<int:id>", methods=['GET','POST'])
@login_required
def edit_user(id):
    admin = User.query.get_or_404(id)
    if current_user.role == 'admin':
        if request.method == "POST":
            current_app.logger.info('Username: %s accessed edit_user', current_user.username)
            admin.username = request.form['username']
            admin.registration = request.form['registration']
            admin.role = request.form['role']
            admin.authorised = request.form['authorised']
            try:
                db.session.commit()
                current_app.logger.info('Username: %s updated user account %s', current_user.username, admin.username)
                flash("User updated successfully")
                return redirect(url_for("admin.admin"))
            except:
                flash("User failed to update")
                current_app.logger.warning('Username: %s failed to update user account %s', current_user.username, admin.username)
                return render_template("edit_user.html", admin=admin)
        else:
            return render_template("edit_user.html", admin=admin)
    else:
        current_app.logger.critical('Username: %s accessed attempted to edit %s account', current_user.username, admin.username)
        return render_template("unauthorised.html")

"""function to delete any users who should no long have access to an account."""
@bp.route("/delete_user/", methods=['GET', 'POST'])
@login_required
def delete_user():
    if current_user.role == 'admin':
        id = request.form.get("id")
        delete_user = User.query.filter_by(id=id).first()
        try:
            db.session.delete(delete_user)
            current_app.logger.warning('Username: %s deleted %s account', current_user.username, delete_user.username)
            db.session.commit()
            flash("User was deleted successfully.")
            return redirect(url_for("admin.admin"))
        except:
            flash("User failed to delete.")
            current_app.logger.warning('Username: %s failed to deleted an account', current_user.username)
            return render_template("admin.html")
    else:
        current_app.logger.critical('Username: %s tried to deleted an account', current_user.username)
        return render_template("unauthorised.html")

"""function to delete tickets, only visiable for admin users"""
@bp.route("/delete_reservation/", methods=['GET', 'POST'])
@login_required
def delete_reservation():
    if current_user.role == 'admin':
        id = request.form.get("id")
        delete_reservation = reserve.query.filter_by(id=id).first()
        try:
            db.session.delete(delete_reservation)
            current_app.logger.warning('Username: %s deleted reservation: %s ', current_user.username, delete_reservation.id)
            db.session.commit()
            flash("Reservation was deleted successfully.")
            return redirect(url_for("main.reservations"))
        except:
            flash("Reservation failed to delete")
            current_app.logger.warning('Username: %s failed to deleted reservation: %s ', current_user.username, delete_reservation.id)
            return redirect(url_for("main.reservations"))
    else:
        current_app.logger.critical('Username: %s tried to deleted a reservation', current_user.username)
        return render_template("unauthorised.html")

@bp.route('/logging_messages')
@login_required
def logging_messages():
    if current_user.role == 'admin':
        log_file_path = 'app.log'
        log_content = read_log_file(log_file_path)

        return render_template('logging_messages.html', log_content=log_content)
    else:
        current_app.logger.critical('Username: %s tried to access log', current_user.username)
        return render_template("unauthorised.html")

def read_log_file(file_path):
    try:
        with open(file_path, 'r') as file:
            log_content = file.read()
        return log_content
    except FileNotFoundError:
        return "Log file not found"