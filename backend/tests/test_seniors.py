import pytest
from datetime import datetime
import json

# Helper that creates a user and returns actual ez_id. Use with app.app_context().
def create_user_and_get_ezid(client, db_user, suffix="001", role=0):
    email = f"user{suffix}@example.com"
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            register(
                email: "{email}",
                role: {role},
                password: "pass123",
                confirmPassword: "pass123",
                name: "User {suffix}",
                phoneNum: "123456{suffix.zfill(4)}"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    user = db_user.query.filter_by(email=email).first()
    assert user is not None, "User not found in database after registration"
    return email, user.ez_id

# ================= QUERY TESTS =================
def test_get_seniors_empty(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            getSeniors {
                senId
                ezId
                gender
                address
            }
        }
        '''
    })
    data = response.get_json()["data"]["getSeniors"]
    assert data == []

def test_get_seniors_with_data(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "001", 0)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{ez_id}",
                gender: "Male",
                dob: "1950-01-01T00:00:00",
                address: "123 Test St",
                pincode: "12345",
                alternatePhoneNum: "9876543210",
                medicalInfo: "{{\\"allergies\\": \\"none\\"}}"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    response = client.post("/graphql", json={
        "query": '''
        query {
            getSeniors {
                senId
                ezId
                gender
                address
                pincode
            }
        }
        '''
    })
    data = response.get_json()["data"]["getSeniors"]
    assert len(data) == 1
    assert data[0]["gender"] == "Male"

def test_get_senior_valid_id(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "002", 0)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{ez_id}",
                gender: "Female",
                dob: "1945-06-15T00:00:00",
                address: "456 Oak Ave",
                pincode: "67890",
                alternatePhoneNum: "5555555555"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    response = client.post("/graphql", json={
        "query": '''
        query {
            getSenior(senId: 1) {
                senId
                ezId
                gender
                address
            }
        }
        '''
    })
    data = response.get_json()["data"]["getSenior"]
    assert data is not None
    assert data["gender"] == "Female"

def test_get_senior_invalid_id(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            getSenior(senId: 999) {
                senId
                ezId
            }
        }
        '''
    })
    data = response.get_json()["data"]["getSenior"]
    assert data is None

# ================= MUTATION TESTS - ADD SENIOR =================
def test_add_senior_success(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "003", 0)
    response = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{ez_id}",
                gender: "Male",
                dob: "1940-12-25T00:00:00",
                address: "789 Pine Rd",
                pincode: "54321",
                alternatePhoneNum: "1111111111",
                medicalInfo: "{{\\"diabetes\\": true, \\"hypertension\\": false}}"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = response.get_json()["data"]["addSenior"]
    assert data["status"] == 201
    assert "success" in data["message"].lower()

def test_add_senior_duplicate(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "004", 0)
    mutation = f'''
    mutation {{
        addSenior(
            ezId: "{ez_id}",
            gender: "Male",
            dob: "1940-12-25T00:00:00",
            address: "789 Pine Rd",
            pincode: "54321",
            alternatePhoneNum: "1111111111"
        ) {{
            status
            message
        }}
    }}
    '''
    client.post("/graphql", json={"query": mutation})
    response = client.post("/graphql", json={"query": mutation})
    data = response.get_json()["data"]["addSenior"]
    assert data["status"] == 403
    assert "already exists" in data["message"].lower()

def test_add_senior_wrong_role(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "005", 1)  # role 1, not a senior
    response = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{ez_id}",
                gender: "Female",
                dob: "1950-01-01T00:00:00",
                address: "123 Test St",
                pincode: "12345",
                alternatePhoneNum: "9876543210"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = response.get_json()["data"]["addSenior"]
    assert data["status"] == 403 or data["status"] == 404

def test_add_senior_user_not_found(client):
    # generate a surely non-existent ez_id
    fake_ez_id = "ez-fake-9999-9999"
    response = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{fake_ez_id}",
                gender: "Male",
                dob: "1950-01-01T00:00:00",
                address: "123 Test St",
                pincode: "12345",
                alternatePhoneNum: "9876543210"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = response.get_json()["data"]["addSenior"]
    assert data["status"] == 404
    assert "user not found" in data["message"].lower()

def test_add_senior_missing_ezid(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            addSenior(
                gender: "Male",
                dob: "1950-01-01T00:00:00",
                address: "123 Test St",
                pincode: "12345",
                alternatePhoneNum: "9876543210"
            ) {
                status
                message
            }
        }
        '''
    })
    assert "errors" in response.get_json()

# ================= MUTATION TESTS - UPDATE SENIOR =================
def test_update_senior_success(client, db_user, app):
    with app.app_context():
        _, ez_id = create_user_and_get_ezid(client, db_user, "006", 0)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{ez_id}",
                gender: "Female",
                dob: "1955-03-10T00:00:00",
                address: "Original Address",
                pincode: "00000",
                alternatePhoneNum: "0000000000"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            updateSenior(
                senId: 1,
                address: "Updated Address",
                pincode: "11111",
                alternatePhoneNum: "1111111111",
                medicalInfo: "{\\"updated\\": true}"
            ) {
                status
                message
            }
        }
        '''
    })
    data = response.get_json()["data"]["updateSenior"]
    assert data["status"] == 1
    assert "successfully" in data["message"].lower()

def test_update_senior_not_found(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            updateSenior(
                senId: 999,
                address: "New Address",
                pincode: "55555",
                alternatePhoneNum: "1111111111"
            ) {
                status
                message
            }
        }
        '''
    })
    data = response.get_json()["data"]["updateSenior"]
    assert data["status"] == 0 or data["status"] == 404

def test_update_senior_missing_senid(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            updateSenior(
                address: "New Address"
            ) {
                status
                message
            }
        }
        '''
    })
    assert "errors" in response.get_json()
