from flask import flash, redirect, render_template, request, url_for
from app.models.models import User
from app.user.forms import LoginForm
from app.extensions import db, bcrypt
from app.user.forms import RegisterForm, LoginForm
from flask_login import current_user, login_required, login_user, logout_user
from app.user import bp


"""function to log into booker"""
@bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main.reserve_parking'))
            else:
                flash("You have entered an incorrect username or password. Please try again.")
        else:
            flash('No username found. Please register an account.')
            return render_template("login.html", form=form)
    return render_template('login.html', form=form)

"""function to register a user for resolve"""
@bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, registration = form.registration.data, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully. Please log in.")
            return redirect(url_for('user.login'))
        except: 
            flash("There has been a problem creating your user. Please contact system administration for assistance.")
            return render_template("register.html")
       
    return render_template('register.html', form=form)

@bp.route("/manage_account", methods=['GET', 'POST'])
@login_required
def manage_account():
    account = User.query.filter_by(username=current_user.username).all()
    return render_template('manage_account.html', account=account)


@bp.route("/edit_account/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_account(id):
    edit_account = User.query.get_or_404(id)
    if request.method == "POST":
        edit_account.username = request.form['username']
        edit_account.registration = request.form['registration']
        try:
            db.session.commit()
            flash("Account updated successfully")
            return redirect(url_for("user.manage_account"))
        except:
            flash("Account failed to update")
            return render_template("manage_account.html", edit_account=edit_account)        
    else:
        return render_template("edit_account.html", edit_account=edit_account)

"""function to log out of resolve"""
@bp.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))