import bcrypt
import pytest

from app.models.models import User, reserve

"""Test admin page cannot be accessed by a normal user"""
def test_normal_user_cannot_access_admin(client): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response = client.get("/admin",follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data

"""Test admin page can be accessed by admin"""
def test_admin_can_access_admin(client): 
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response = client.get("/admin",follow_redirects=True)
    assert b'Admin' in response.data

"""Test altering role"""
def test_change_user_role(client, app):
    client.post('/', data={"username": "admin", "password": "Assignment1/"}, follow_redirects = True)
    client.get("/admin") 
    client.get('/edit_user/1')

    response = client.post('/edit_user/1', data={"username":"testuser","registration":"TE33 SER","role": "admin","authorised":"Y"}, follow_redirects = True)
    assert b'User updated successfully'in response.data
    with app.app_context():
        user =User.query.filter_by(username='testuser',role='admin').first()
        assert user is not None

"""Test a user cannot alter a role"""
def test_change_user_role_as_user(client, app):
    client.post('/', data={"username": "testuser", "password": "Assignment1/"}, follow_redirects = True)

    response = client.get('/edit_user/1', follow_redirects = True)
    assert b'You are not authorised to access this page'in response.data
    

"""Test expection handling when editing user"""
def test_error_editing_user(client):
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    
    with pytest.raises(Exception):
        response = client.post("/edit_user/1", data={"username": "testuser","registration": "TE38 SER"},follow_redirects=True)
        assert b'User failed to update' in response.data


"""Test changing account to authorised"""
def test_authorise_user(client, app):
    client.post("/register/", data={"username": "testuser1", "registration": "TE30 SER", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post('/', data={"username": "testuser1", "password": "Assignment1/"}, follow_redirects = True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.' in response.data
    
    client.post('/', data={"username": "admin", "password": "Assignment1/"}, follow_redirects = True)
    client.get("/admin") 
    response = client.post('/edit_user/3', data={"username":"testuser1","registration":"TE30 SER","role": "admin","authorised":"Y"}, follow_redirects = True)
    assert b'User updated successfully'in response.data
    
    response= client.post('/', data={"username": "testuser1", "password": "Assignment1/"}, follow_redirects = True)
    assert b'<p>Welcome to Booker.</p>'in response.data
    
    with app.app_context():
        user =User.query.filter_by(username='testuser1',authorised='Y').first()
        assert user is not None

"""Test changing account to unauthorised"""
def test_unauthorise_user(client, app):
    response= client.post('/', data={"username": "testuser", "password": "Assignment1/"}, follow_redirects = True)
    assert b'<p>Welcome to Booker.</p>'in response.data
    
    client.post('/', data={"username": "admin", "password": "Assignment1/"}, follow_redirects = True)
    client.get("/admin") 
    response = client.post('/edit_user/1', data={"username":"testuser","registration":"TE33 SER","role": "admin","authorised":"N"}, follow_redirects = True)
    assert b'User updated successfully'in response.data
    
    response= client.post('/', data={"username": "testuser1", "password": "Assignment1/"}, follow_redirects = True)
    assert b'Unsucessful sign in. Either username/password incorrect, account locked or unauthorised.' in response.data
    
    with app.app_context():
        user =User.query.filter_by(username='testuser',authorised='N').first()
        assert user is not None

"""Test deleting a user"""
def test_delete_user(client,app): 
    client.post('/', data={"username": "admin", "password": "Assignment1/"}, follow_redirects = True)
    response= client.post('/delete_user/', data= {"id":"1"}, follow_redirects=True)
    assert b'User was deleted successfully.' in response.data
    with app.app_context():
        user =User.query.filter_by(username='testuser').first()
        assert user is None

"""Test expection handling when deleting user"""
def test_error_deleting_user(client):
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    
    with pytest.raises(Exception):
        response = client.post('/delete_user/', data= {"id":"1"}, follow_redirects=True)
        assert b'User failed to delete' in response.data

"""Test deleting a user by another user doesnt work"""
def test_delete_user_by_user(client,app): 
    client.post('/', data={"username": "testuser", "password": "Assignment1/"}, follow_redirects = True)
    response= client.post('/delete_user/', data= {"id":"2"}, follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data
    with app.app_context():
        user =User.query.filter_by(username='admin').first()
        assert user is not None

"""test deleting a reservation"""
def test_delete_reservation(client,app): 
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"admin","registration":"AD70 MIN","date":"2024-02-29"} , follow_redirects=True)


    response= client.post('/delete_reservation/', data= {"id":"1"}, follow_redirects=True)
    assert b'Reservation was deleted successfully.' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1').first()
        assert user is None

"""test a user cannot delete a reservation"""
def test_user_delete_reservation(client,app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)

    response= client.post('/delete_reservation/', data= {"id":"1"}, follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1').first()
        assert user is not None

"""Test expection handling when deleting reservation"""
def test_error_deleting_reservation(client):
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    
    with pytest.raises(Exception):
        response = client.post('/delete_user/', data= {"id":"1"}, follow_redirects=True)
        assert b'Reservation failed to delete' in response.data

"""logging messages
def test_logging_messages(client): 
    response= client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    print(response.data)
    assert b'Username: admin logged in successfully' in response.data
"""
