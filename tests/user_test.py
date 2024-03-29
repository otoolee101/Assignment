import time
import pytest
from app.extensions import db, bcrypt
from app.models.models import User

"""Test login page appears"""
def test_login_page(client):
    response = client.get('/')
    assert b'<h1>Login Page</h1>' in response.data

"""Test registering a new user"""    
def test_register_new_users(client, app):
    response = client.post("/register/", data={"username": "testuser1", "registration": "TE30 SER", "password": "Assignment1/"}, follow_redirects=True)
    assert b'User created successfully. Please log in.' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None

"""Test registering a new user but not having a Upper case letter, number and special character"""    
def test_register_user_password_constraints(client):
    response = client.post("/register/", data={"username": "testuser", "registration": "TE33 SER", "password": "password"}, follow_redirects=True)
    print(response.data)
    assert b'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character' in response.data
   
"""Test registering a new user with not a unique username"""    
def test_register_unique_username(client):
    client.post("/register/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment1/"})
    response = client.post("/register/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment1/"}, follow_redirects=True)
    assert b'User already exists' in response.data

"""Test logging into Booker when an account is authorised """
def test_logging_in_authorised(client, app):
    response = client.post("/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment1/"}, follow_redirects=True)
    assert b'<p>Welcome to Booker.</p>' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser', authorised='Y').first()
        assert user is not None

"""Test logging into Booker when an account is not authorised """
def test_logging_in_unauthorised(client,app): 
    client.post("/register/", data={"username": "testuser1", "registration": "TE30 SER", "password": "Assignment1/"})
    response = client.post("/", data={"username": "testuser1", "password": "Assignment1/"}, follow_redirects=True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser1', authorised='N').first()
        assert user is not None

"""Test logging in without an account registered"""
def test_logging_in_without_an_account(client,app): 
    response = client.post("/", data={"username": "testuser1", "registration": "TE33 SER", "password": "Assignment1/"}, follow_redirects=True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser1').first()
        assert user is None

"""Test expection handling when registering an account"""
def test_error_registering_user(client):
    response = client.get('/register/')
    assert b'<h1>Register Page</h1>' in response.data

    with pytest.raises(Exception):
        response = client.post("/register/", data = {"username": "testuser", "registration": "TE33 SER", "password": "Assignment1/"}, follow_redirects=True)
        assert b'There has been a problem creating your user. Please contact system administration for assistance.' in response.data

"""Test entering an incorrect password into an exisiting user"""
def test_incorrect_password(client): 
    response = client.post("/", data={"username": "testuser", "password": "Assignment2/"}, follow_redirects=True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised'in response.data

"""test account locks after 3 inccorect password attempts"""
def test_locked_account(client, app): 
    client.post("/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment2/"}, follow_redirects=True)
    client.post("/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment3/"}, follow_redirects=True)
    response = client.post("/", data={"username": "testuser", "registration": "TE33 SER", "password": "Assignment4/"}, follow_redirects=True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised'in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser', authorised='N', failed_login_attempts = 3 ).first()
        assert user is not None

"""Test failed login attempts resets to 0 when password entered successfully"""
def test_reset_of_failed_login_attempts(client, app): 
    user=User(username='testuser1', registration='TE30 SER', password=bcrypt.generate_password_hash('Assignment1/'), role='user', authorised = 'Y', failed_login_attempts = 2)
    db.session.add(user)
    db.session.commit()
    response = client.post("/", data={"username": "testuser1", "password": "Assignment1/"}, follow_redirects=True)
    assert b'<p>Welcome to Booker.</p>' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser1', authorised='Y', failed_login_attempts = 0 ).first()
        assert user is not None
    
"""Test that a user can update their own registration"""
def test_update_registration(client, app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response = client.post("/edit_account/1", data={"username": "testuser","registration": "TE38 SER"},follow_redirects=True)
    assert b'Account updated successfully' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser', registration='TE38 SER' ).first()
        assert user is not None

"""Test that a user cannot alter someone elses account """
def test_update_registration_of_another_account(client, app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response = client.post("/edit_account/2", data={"username": "testuser","registration": "TE38 SER"},follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data
    with app.app_context():
        user = User.query.filter_by(username='testuser', registration='TE33 SER' ).first()
        assert user is not None

"""Test expection handling when editing an account"""
def test_error_editing_account(client):
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    
    with pytest.raises(Exception):
        response = client.post("/edit_account/1", data={"username": "testuser","registration": "TE38 SER"},follow_redirects=True)
        assert b'Account failed to update' in response.data

"""Test logout"""
def test_logout(client): 
    response = client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    
    assert b'<p>Welcome to Booker.</p>' in response.data

    response = client.get('/logout/', follow_redirects=True)
    assert b'<h1>Login Page</h1>' in response.data

"""Test booker times out after 60 seconds of inactivity
def test_timeout(client): 
    response = client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    assert b'<p>Welcome to Booker.</p>' in response.data
    time.sleep(30)
    responses= client.get("/reserve_parking")
    assert b'<h1>Login Page</h1>' in responses.data
    """
