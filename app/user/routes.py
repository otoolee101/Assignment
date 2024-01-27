from flask import flash, redirect, render_template, url_for
from app.models.models import User
from app.user.forms import LoginForm
from app.extensions import db, bcrypt
from app.user.forms import RegisterForm, LoginForm
from flask_login import login_required, login_user, logout_user
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
                return redirect(url_for('main.home'))
            else:
                flash("You have entered an incorrect username or password. Please try again.")
        else:
            flash('No username found. Please register an account.')
            return render_template("user/login.html", form=form)
    return render_template('login.html', form=form)

"""function to register a user for resolve"""
@bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully. Please log in.")
            return redirect(url_for('user.login'))
        except: 
            flash("There has been a problem creating your user. Please contact system administration for assistance.")
            return render_template("user/register.html")
        
    return render_template('register.html', form=form)

@bp.route("/user")
def user():
    return render_template("user.html") 

"""function to log out of resolve"""
@bp.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))