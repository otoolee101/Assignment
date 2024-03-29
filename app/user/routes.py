from datetime import timedelta
from flask import current_app, flash, redirect, render_template, request, session, url_for
from app.main.routes import check_authorisation
from app.models.models import User
from app.extensions import db, bcrypt
from app.user.forms import RegisterForm, LoginForm
from flask_login import current_user, login_required, login_user, logout_user
from app.user import bp

#End session if no activity has occured within 60 seconds 
@bp.before_app_request  
def make_session_permanent():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(seconds=60)

#Function to Login to Booker
@bp.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try: 
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash( user.password, form.password.data):
                    session.permanent = True

                    #rrun reset login function is password correct
                    reset_login_attempts(user)  

                    #If user authorised take them to the reservation page 
                    if user.authorised == 'Y':
                        current_app.logger.info('Username: %s logged in successfully', user.username)
                        return redirect(url_for('main.reserve_parking'))
                    
                    #If users not authorised do not let them in. 
                    else:
                        current_app.logger.info('Username: %s attempted to log in but not yet authorised', user.username)
                        flash ("Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.")
                        return redirect(url_for('user.login'))
                    
                else:
                    #If login attempt failed run failed login function 
                    failed_login(user)
            else:
                flash ("Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.")
                current_app.logger.warning('There was a failed attempt to login.')
                return render_template("login.html", form=form)
            
        except Exception as e:
            flash("An error occurred during login. Please try again.")
            current_app.logger.exception('Error during login: %s', str(e))
            return redirect(url_for('user.login'))
        
    return render_template('login.html', form=form)

#On each failed login attempt increase there failed_login_attempts by 1. 
#If it greater or equal to 3 failed login attempts, lock the account
def failed_login(user):
    user.failed_login_attempts += 1
    current_app.logger.warning('Username: %s has a failed login attempt', user.username)
    db.session.commit()
    if user.failed_login_attempts >= 3:
        user.authorised = 'N'
        current_app.logger.critical('Username: %s has locked their account', user.username)
        flash ("Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.")
        db.session.commit()
    else:
        flash ("Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.")

#reset failed login attempts back to 0 if password correct
def reset_login_attempts(user):
    user.failed_login_attempts = 0
    db.session.commit()
    login_user(user) 


#Function to register a user for Booker
@bp.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, registration = form.registration.data, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info('Username: %s successfully created an account', new_user.username)
            flash("User created successfully. Please log in.")
            return redirect(url_for('user.login'))
        
        except Exception as e: 
            flash("There has been a problem creating your user. Please contact system administration for assistance.")
            current_app.logger.warning('Failure to create a user account')
            return render_template("register.html")
       
    return render_template('register.html', form=form)

#Function to retrieve users own account
@bp.route("/manage_account", methods=['GET', 'POST'])
@login_required
@check_authorisation
def manage_account():
    try:
        #Check current username matches and return username it matches
        account = User.query.filter_by(username=current_user.username).all()
        current_app.logger.info('Username: %s accessed manage_account', current_user.username)
        return render_template('manage_account.html', account=account)
    
    except Exception as e:
                flash("There has been an error loading manage accounts ")
                current_app.logger.warning('Username: %s had a failure loading manage accounts', current_user.username)
                return redirect(url_for('user.reserve_parking'))  
    
#Function to edit own user account in Booker, e.g. update registration
@bp.route("/edit_account/<int:id>", methods=['POST', 'GET'])
@login_required
def edit_account(id):
    edit_user = User.query.get_or_404(id)

    #Gets the current username of the person logged and the username of the account getting updated 
    #and if they dont match it will not allow updates.
    if current_user.authorised =='Y' and current_user.username == edit_user.username:
        edit_account = User.query.get_or_404(id)

        if request.method == "POST":
            current_app.logger.info('Username: %s accessed edit_account', current_user.username)
            edit_account.username = request.form['username']
            edit_account.registration = request.form['registration']

            try:
                #Try save update to the database
                db.session.commit()
                flash("Account updated successfully")
                current_app.logger.info('Username: %s successfully edited account %s', current_user.username, edit_user.username)
                return redirect(url_for("user.manage_account"))
            except Exception as e:
                flash("Account failed to update")
                current_app.logger.warning('Username: %s failed to edited account %s', current_user.username, edit_user.username)
                return render_template("manage_account.html", edit_account=edit_account)        
            
        else:
            return render_template("edit_account.html", edit_account=edit_account)
        
    else: 
        current_app.logger.critical('Username: %s attempted to edit %s account', current_user.username, edit_user.username)
        flash("You are not authorised to access this page")
        return redirect(url_for('user.manage_account'))


#Function to log out of Booker
@bp.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    current_app.logger.info('Username: %s logged out', current_user.username)
    logout_user()
    return redirect(url_for('user.login'))