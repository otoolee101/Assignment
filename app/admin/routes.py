from flask import render_template
from app.admin import bp

@bp.route("/admin")
def admin():
    return render_template("admin.html") 