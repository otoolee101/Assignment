from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.admin import bp
from app.models.models import User
from app.extensions import db
    
"""Function to return all user account when you are loggined in as a admin user."""
@bp.route("/admin/")
@login_required
def admin():
    if current_user.role == 'admin':
        admin= User.query.all()
        return render_template('admin.html',admin=admin)
    else:
        flash("You do not have the correct permissions to view admin page. Please contact system adminstrator.")
        return render_template("reserve_parking.html")
    
"""Function to be able to edit a username or role"""
@bp.route("/edit_user/<int:id>", methods=['GET','POST'])
@login_required
def edit_user(id):
    if current_user.role == 'admin':
        admin = User.query.get_or_404(id)
        if request.method == "POST":
            admin.username = request.form['username']
            admin.role = request.form['role']
            try:
                db.session.commit()
                flash("User updated successfully")
                return redirect(url_for("admin.admin"))
            except:
                flash("User failed to update")
                return render_template("edit_user.html", admin=admin)
        else:
            return render_template("edit_user.html", admin=admin)
    else:
        flash("You do not have the correct permissions to edit user accounts. Please contact your system adminstrator.")

"""function to delete any users who should no long have access to an account."""
@bp.route("/delete_user/", methods=['GET', 'POST'])
@login_required
def delete_user():
    if current_user.role == 'admin':
        id = request.form.get("id")
        delete_user = User.query.filter_by(id=id).first()
        try:
            db.session.delete(delete_user)
            db.session.commit()
            flash("User was deleted successfully.")
            return redirect(url_for("admin.admin"))
        except:
            flash("User failed to delete.")
            return render_template("reserve_parking.html")
    else:
        flash("You do not have the correct permissions to delete this user. Please contact system adminstrator.")
        return render_template("admin.html")
