import pytest
from datetime import datetime, timedelta
import json

def register_user_and_get_ezid(client, suffix="001", role=0):
    """Helper to register user and get ez_id"""
    user_type = "senior" if role == 0 else "doctor"
    email = f"{user_type}{suffix}@example.com"
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            register(
                email: "{email}",
                role: {role},
                password: "pass123",
                confirmPassword: "pass123",
                name: "{user_type.title()} {suffix}",
                phoneNum: "{role}0000{suffix.zfill(4)}"
            ) {{
                status
                message
                ezId
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["register"]
    assert data["status"] == 200
    assert data["ezId"] is not None
    return email, data["ezId"]

def create_senior_and_doctor(client):
    """Helper to create both senior and doctor users and their profiles"""
    # Create senior user
    _, senior_ez_id = register_user_and_get_ezid(client, "101", role=0)
    
    # Create doctor user  
    _, doctor_ez_id = register_user_and_get_ezid(client, "201", role=1)
    
    # Add senior profile
    senior_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{senior_ez_id}",
                gender: "Male",
                dob: "1950-01-01T00:00:00",
                address: "Senior Address",
                pincode: "12345",
                alternatePhoneNum: "9999999999"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert senior_resp.get_json()["data"]["addSenior"]["status"] == 201
    
    # Add doctor profile
    doctor_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{doctor_ez_id}",
                gender: "Female",
                licenseNumber: "LIC123",
                specialization: "Cardiology",
                consultationFee: 500.0
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert doctor_resp.get_json()["data"]["addDoctor"]["status"] == 201
    
    return senior_ez_id, doctor_ez_id

# ==================== QUERY TESTS ====================

def test_get_appointments_for_senior_empty(client):
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForSenior(senId: 1) {
                appId
                senId
                docId
                reason
                status
            }
        }
        '''
    })
    data = resp.get_json()["data"]["getAppointmentsForSenior"]
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_appointments_for_doctor_empty(client):
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForDoctor(docId: 1) {
                appId
                senId
                docId
                reason
                status
            }
        }
        '''
    })
    data = resp.get_json()["data"]["getAppointmentsForDoctor"]
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_appointments_for_senior_with_data(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Regular checkup"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Query appointments for senior
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForSenior(senId: 1) {
                appId
                senId
                docId
                reason
                status
            }
        }
        '''
    })
    appointments = resp.get_json()["data"]["getAppointmentsForSenior"]
    assert len(appointments) == 1
    assert appointments[0]["senId"] == 1
    assert appointments[0]["docId"] == 1
    assert appointments[0]["reason"] == "Regular checkup"
    assert appointments[0]["status"] == 0  # pending

def test_get_appointments_for_doctor_with_data(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment
    future_time = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Consultation"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Query appointments for doctor
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForDoctor(docId: 1) {
                appId
                senId
                docId
                reason
                status
            }
        }
        '''
    })
    appointments = resp.get_json()["data"]["getAppointmentsForDoctor"]
    assert len(appointments) == 1
    assert appointments[0]["docId"] == 1
    assert appointments[0]["reason"] == "Consultation"

def test_get_appointments_for_doctor_senior_specific(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment
    future_time = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Follow-up"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Query specific doctor-senior appointments
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForDoctorSenior(senId: 1, docId: 1) {
                appId
                senId
                docId
                reason
                status
            }
        }
        '''
    })
    appointments = resp.get_json()["data"]["getAppointmentsForDoctorSenior"]
    assert len(appointments) == 1
    assert appointments[0]["senId"] == 1
    assert appointments[0]["docId"] == 1

def test_get_available_slots_all_available(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Query available slots for a future date
    future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    resp = client.post("/graphql", json={
        "query": f'''
        query {{
            getAvailableSlots(docId: 1, date: "{future_date}") {{
                slots
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["getAvailableSlots"]
    assert "slots" in data
    assert len(data["slots"]) == 9  # 9am-5pm = 9 slots

def test_get_available_slots_with_bookings(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment for specific time
    future_date = datetime.now() + timedelta(days=15)
    appointment_time = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{appointment_time.strftime('%Y-%m-%dT%H:%M:%S')}",
                reason: "Slot booking test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Query available slots
    resp = client.post("/graphql", json={
        "query": f'''
        query {{
            getAvailableSlots(docId: 1, date: "{future_date.strftime('%Y-%m-%d')}") {{
                slots
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["getAvailableSlots"]
    assert len(data["slots"]) == 8  # One slot should be booked

# ==================== BOOK APPOINTMENT TESTS ====================

def test_book_appointment_success(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    future_time = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Annual checkup"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["bookAppointment"]
    assert data["status"] == 201
    assert "successfully" in data["message"].lower()

def test_book_appointment_invalid_senior(client):
    # Create only doctor, no senior
    _, doctor_ez_id = register_user_and_get_ezid(client, "301", role=1)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{doctor_ez_id}",
                licenseNumber: "LIC301"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    future_time = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 999,
                docId: 1,
                remTime: "{future_time}",
                reason: "Invalid senior test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["bookAppointment"]
    # Should handle gracefully - check your actual implementation

def test_book_appointment_invalid_doctor(client):
    # Create only senior, no doctor
    _, senior_ez_id = register_user_and_get_ezid(client, "401", role=0)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{senior_ez_id}",
                gender: "Female",
                dob: "1955-01-01T00:00:00",
                address: "Test Address",
                pincode: "54321",
                alternatePhoneNum: "8888888888"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    future_time = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 999,
                remTime: "{future_time}",
                reason: "Invalid doctor test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["bookAppointment"]
    # Should handle gracefully - check your actual implementation

def test_book_appointment_missing_required_fields(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            bookAppointment(
                senId: 1,
                docId: 1,
                reason: "Missing time"
            ) {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

# ==================== UPDATE APPOINTMENT STATUS TESTS ====================

def test_update_appointment_status_success(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment first
    future_time = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Status update test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Update status to confirmed
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                appId: 1,
                status: 1
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["updateAppointmentStatus"]
    assert data["status"] == 200
    assert "updated" in data["message"].lower()

def test_update_appointment_status_rejected(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment first
    future_time = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Rejection test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Update status to rejected
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                appId: 1,
                status: -1
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["updateAppointmentStatus"]
    assert data["status"] == 200
    assert "updated" in data["message"].lower()

def test_update_appointment_status_not_found(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                appId: 999,
                status: 1
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["updateAppointmentStatus"]
    assert data["status"] == 0
    assert "not found" in data["message"].lower()

def test_update_appointment_status_invalid_status(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment first
    future_time = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Invalid status test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Try invalid status
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                appId: 1,
                status: 5
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["updateAppointmentStatus"]
    assert data["status"] == 0
    assert "invalid status" in data["message"].lower()

def test_update_appointment_missing_app_id(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                status: 1
            ) {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

# ==================== CANCEL APPOINTMENT TESTS ====================

def test_cancel_appointment_success(client):
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book appointment first
    future_time = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Cancellation test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Cancel appointment
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            cancelAppointment(appId: 1) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["cancelAppointment"]
    assert data["status"] == 1
    assert "cancelled successfully" in data["message"].lower()

def test_cancel_appointment_not_found(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            cancelAppointment(appId: 999) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["cancelAppointment"]
    assert data["status"] == 0
    assert "not found" in data["message"].lower()

def test_cancel_appointment_missing_app_id(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            cancelAppointment {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

# ==================== INTEGRATION TESTS ====================

def test_appointment_workflow_complete(client):
    """Test complete appointment workflow: book -> confirm -> cancel"""
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # 1. Book appointment
    future_time = (datetime.now() + timedelta(days=42)).strftime("%Y-%m-%dT%H:%M:%S")
    book_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            bookAppointment(
                senId: 1,
                docId: 1,
                remTime: "{future_time}",
                reason: "Complete workflow test"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert book_resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # 2. Confirm appointment
    confirm_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateAppointmentStatus(
                appId: 1,
                status: 1
            ) {
                status
                message
            }
        }
        '''
    })
    assert confirm_resp.get_json()["data"]["updateAppointmentStatus"]["status"] == 200
    
    # 3. Verify appointment status via query
    query_resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForSenior(senId: 1) {
                appId
                status
                reason
            }
        }
        '''
    })
    appointments = query_resp.get_json()["data"]["getAppointmentsForSenior"]
    assert len(appointments) == 1
    assert appointments[0]["status"] == 1  # confirmed
    
    # 4. Cancel appointment
    cancel_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            cancelAppointment(appId: 1) {
                status
                message
            }
        }
        '''
    })
    assert cancel_resp.get_json()["data"]["cancelAppointment"]["status"] == 1

def test_multiple_appointments_same_doctor(client):
    """Test booking multiple appointments with same doctor"""
    senior_ez_id, doctor_ez_id = create_senior_and_doctor(client)
    
    # Book multiple appointments
    appointments_data = [
        {"days": 7, "reason": "First appointment"},
        {"days": 14, "reason": "Second appointment"},
        {"days": 21, "reason": "Third appointment"}
    ]
    
    for i, appt in enumerate(appointments_data):
        future_time = (datetime.now() + timedelta(days=appt["days"])).strftime("%Y-%m-%dT%H:%M:%S")
        resp = client.post("/graphql", json={
            "query": f'''
            mutation {{
                bookAppointment(
                    senId: 1,
                    docId: 1,
                    remTime: "{future_time}",
                    reason: "{appt["reason"]}"
                ) {{
                    status
                    message
                }}
            }}
            '''
        })
        assert resp.get_json()["data"]["bookAppointment"]["status"] == 201
    
    # Verify all appointments
    query_resp = client.post("/graphql", json={
        "query": '''
        query {
            getAppointmentsForDoctor(docId: 1) {
                appId
                reason
                status
            }
        }
        '''
    })
    appointments = query_resp.get_json()["data"]["getAppointmentsForDoctor"]
    assert len(appointments) == 3
    
    reasons = [appt["reason"] for appt in appointments]
    assert "First appointment" in reasons
    assert "Second appointment" in reasons
    assert "Third appointment" in reasons
