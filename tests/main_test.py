import pytest
from app.models.models import reserve

"""Create a reservation"""
def test_create_reservation(client,app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1').first()
        assert user is not None

"""Test error handling for creating reservation"""
def test_error_create_reservation(client):
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    
    with pytest.raises(Exception):
        response= client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
        assert b'Reservation failed to create. Please contact system administration.' in response.data

"""Test that only 5 reservations can be created for any singluar date"""
def test_reservations_full(client):
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    
    response= client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'All parking spaces for this date are booked. Please select another date.' in response.data

"""Test if 5 booking are in the system already and one is canceled another booking can then be made"""
def test_book_reservation_after_cancellation(client): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    response= client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'All parking spaces for this date are booked. Please select another date.' in response.data

    response= client.post("/cancel_reservation/", data= {"id":"1"}, follow_redirects=True)
    assert b'Reservation cancelled successfully.' in response.data

    response=client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data

"""Test only the user logged in can view their own bookings"""
def test_user_reservation_view(client):
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"admin","registration":"AD70 MIN","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data

    response = client.get("/reservations")
    assert b'<td>TE33 SER</td>' in response.data
    assert b'<td>AD70 MIN</td>' not in response.data

"""Test admin can see allow reservations made in Booker"""
def test_admin_reservation_view(client):
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"admin","registration":"AD70 MIN","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data

    response = client.get("/reservations")
    assert b'<td>TE33 SER</td>' in response.data
    assert b'<td>AD70 MIN</td>' in response.data

"""User editing a reservation they have created"""
def test_user_editing_own_reservation(client, app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data

    response= client.post("/edit_reservations/1",data= {"username":"testuser","registration":"TE33 SER","date":"2024-02-28" }, follow_redirects=True)
    assert b'Reservation updated successfully' in response.data 
    with app.app_context():
        user =reserve.query.filter_by(id='1', date = "2024-02-28").first()
        assert user is not None

"""Admin editing any reservation """
def test_admin_editing_reservation(client, app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post("/edit_reservations/1",data= {"username":"testuser","registration":"TE33 SER","date":"2024-02-28" }, follow_redirects=True)
    assert b'Reservation updated successfully' in response.data 
    with app.app_context():
        user =reserve.query.filter_by(id='1', date = "2024-02-28").first()
        assert user is not None

"""Testing that a user canot edit a reservation belonging to a different user"""
def test_user_editing_different_reservation(client, app): 
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response =client.post("/reserve_parking",data={"username":"admin","registration":"AD70 MIN","date":"2024-02-29"} , follow_redirects=True)
    assert b'Reservation created successfully.' in response.data
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post("/edit_reservations/1",data= {"username":"admin","registration":"AD70 MIN","date":"2024-02-28" }, follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data 
    with app.app_context():
        user =reserve.query.filter_by(id='1', date = "2024-02-29").first()
        assert user is not None

"""Test error handling for editing reservation"""
def test_error_editing_reservation(client):
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    
    with pytest.raises(Exception):
        response= client.post("/edit_reservations/1",data= {"username":"admin","registration":"AD70 MIN","date":"2024-02-28" }, follow_redirects=True)
        assert b'Reservation failed to update.' in response.data

"""Test user can cancel their own reservation"""
def test_user_cancel_reservation(client,app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    response= client.post("/cancel_reservation/", data= {"id":"1"}, follow_redirects=True)
    assert b'Reservation cancelled successfully.' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1', cancelled = 'Y').first()
        assert user is not None

"""Test admin can cancel any reservation"""
def test_admin_cancel_reservation(client,app): 
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post("/cancel_reservation/", data= {"id":"1"}, follow_redirects=True)
    assert b'Reservation cancelled successfully.' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1', cancelled = 'Y').first()
        assert user is not None

"""Test a user cant cancel another users reservation reservation"""
def test_user_canceling_different_reservation(client,app): 
    client.post("/", data={"username": "admin", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"admin","registration":"AD70 MIN","date":"2024-02-29"} , follow_redirects=True)
    client.post("/logout/",follow_redirects=True)

    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    response= client.post("/cancel_reservation/", data= {"id":"1"}, follow_redirects=True)
    assert b'You are not authorised to access this page' in response.data
    with app.app_context():
        user =reserve.query.filter_by(id='1', cancelled = 'N').first()
        assert user is not None

"""Test error handling for cancelling reservation"""
def test_error_cancel_reservation(client):
    client.post("/", data={"username": "testuser", "password": "Assignment1/"}, follow_redirects=True)
    client.post("/reserve_parking",data={"username":"testuser","registration":"TE33 SER","date":"2024-02-29"} , follow_redirects=True)
    
    with pytest.raises(Exception):
        response= client.post("/cancel_reservations/1", data= {"id":"1"}, follow_redirects=True)
        assert b'Reservation failed to update' in response.data