from flask import current_app, flash, redirect, render_template, request, url_for
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
                if current_user.authorised =='Y':
                    current_app.logger.info('Username: %s logged in successfully', current_user.username)
                    return redirect(url_for('main.reserve_parking'))
                else:
                    current_user.authorised =='N'
                    current_app.logger.info('Username: %s attempted to log in but not yet authorised', current_user.username)
                    return  render_template('unauthorised.html')
            else:
                flash("Username or password incorrect.")
                current_app.logger.warning('There was failed attempt to login.')
        else:
            flash('Username or password incorrect.')
            current_app.logger.warning('There was a failed attempt to login.')
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
            current_app.logger.info('Username: %s successfully created an account', new_user.username)
            flash("User created successfully. Please log in.")
            return redirect(url_for('user.login'))
        except: 
            flash("There has been a problem creating your user. Please contact system administration for assistance.")
            current_app.logger.warning('Failure to create a user account')
            return render_template("register.html")
       
    return render_template('register.html', form=form)

@bp.route("/manage_account", methods=['GET', 'POST'])
@login_required
def manage_account():
    if current_user.authorised =='Y':
        account = User.query.filter_by(username=current_user.username).all()
        current_app.logger.info('Username: %s accessed manage_account', current_user.username)
        return render_template('manage_account.html', account=account)
    else: 
        current_app.logger.warning('Username: %s failed to access manage_account', current_user.username)
        return render_template("unauthorised.html") 


@bp.route("/edit_account/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_account(id):
    edit_user = User.query.get_or_404(id)
    """Gets the current username of the person logged and the username of the account getting updated 
    and if they dont match it will not allow updates."""
    if current_user.authorised =='Y' and current_user.username == edit_user.username:
        edit_account = User.query.get_or_404(id)
        if request.method == "POST":
            current_app.logger.info('Username: %s accessed edit_account', current_user.username)
            edit_account.username = request.form['username']
            edit_account.registration = request.form['registration']
            try:
                db.session.commit()
                flash("Account updated successfully")
                current_app.logger.info('Username: %s successfully edited account %s', current_user.username, edit_user.username)
                return redirect(url_for("user.manage_account"))
            except:
                flash("Account failed to update")
                current_app.logger.warning('Username: %s failed to edited account %s', current_user.username, edit_user.username)
                return render_template("manage_account.html", edit_account=edit_account)        
        else:
            current_app.logger.warning('Username: %s failed to edited account %s', current_user.username, edit_user.username)
            return render_template("edit_account.html", edit_account=edit_account)
        
    else: 
        current_app.logger.critical('Username: %s attempted to edit %s account', current_user.username, edit_user.username)
        return render_template("unauthorised.html") 


"""function to log out of resolve"""
@bp.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    current_app.logger.info('Username: %s logged out', current_user.username)
    logout_user()
    return redirect(url_for('user.login'))