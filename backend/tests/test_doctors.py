import pytest
import json

def register_user_and_get_ezid(client, suffix="001", role=1):
    # By default, doctors/health professionals have role 1
    email = f"doctor{suffix}@example.com"
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            register(
                email: "{email}",
                role: {role},
                password: "pass123",
                confirmPassword: "pass123",
                name: "Doctor {suffix}",
                phoneNum: "10000{suffix.zfill(4)}"
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

# ================== QUERY TESTS ==================

def test_get_doctors_empty(client):
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getDoctors {
                docId
                ezId
                licenseNumber
            }
        }
        '''
    })
    data = resp.get_json()["data"]["getDoctors"]
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_doctors_with_data(client):
    _, ez_id = register_user_and_get_ezid(client, "101", 1)
    license_num = "LIC101"

    # Add doctor
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Male",
                dob: "1980-05-10T00:00:00",
                address: "Doc Lane",
                pincode: "560001",
                alternatePhoneNum: "9999910101",
                licenseNumber: "{license_num}",
                specialization: "Cardiology",
                affiliation: "{{\\"hospital\\": \\"BestCare\\"}}",
                consultationFee: 750.0
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["addDoctor"]
    assert data["status"] == 201

    # Query all doctors
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getDoctors {
                docId
                ezId
                licenseNumber
                gender
                address
                pincode
                specialization
                consultationFee
            }
        }
        '''
    })
    doctors = resp.get_json()["data"]["getDoctors"]
    assert len(doctors) == 1
    d = doctors[0]
    assert d["licenseNumber"] == "LIC101"
    assert d["specialization"] == "Cardiology"
    assert d["consultationFee"] == 750.0

def test_get_doctor_valid_id(client):
    _, ez_id = register_user_and_get_ezid(client, "102", 1)
    license_num = "LIC102"

    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Female",
                dob: "1985-07-22T00:00:00",
                address: "Med Tower",
                pincode: "560002",
                alternatePhoneNum: "2222244444",
                licenseNumber: "{license_num}",
                specialization: "Neurology"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert resp.get_json()["data"]["addDoctor"]["status"] == 201

    resp2 = client.post("/graphql", json={
        "query": '''
        query {
            getDoctor(docId: 1) {
                docId
                ezId
                licenseNumber
                gender
                specialization
                address
            }
        }
        '''
    })
    doctor = resp2.get_json()["data"]["getDoctor"]
    assert doctor is not None
    assert doctor["licenseNumber"] == "LIC102"
    assert doctor["specialization"] == "Neurology"
    assert doctor["address"] == "Med Tower"

def test_get_doctor_invalid_id(client):
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getDoctor(docId: 999) {
                docId
                ezId
                licenseNumber
            }
        }
        '''
    })
    doctor = resp.get_json()["data"]["getDoctor"]
    assert doctor is None

def test_get_doctors_filter_by_pincode_and_specialization(client):
    # Register and add two doctors, different pincodes/specialties
    _, ez_id1 = register_user_and_get_ezid(client, "201", 1)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id1}",
                gender: "Male",
                licenseNumber: "LIC201",
                pincode: "777001",
                specialization: "Orthopedics"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    _, ez_id2 = register_user_and_get_ezid(client, "202", 1)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id2}",
                gender: "Female",
                licenseNumber: "LIC202",
                pincode: "888002",
                specialization: "Dentistry"
            ) {{
                status
                message
            }}
        }}
        '''
    })

    # Filter by pincode
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getDoctors(pincode: "777001") {
                ezId
                licenseNumber
                specialization
                pincode
            }
        }
        '''
    })
    docs = resp.get_json()["data"]["getDoctors"]
    assert len(docs) == 1 and docs[0]["specialization"] == "Orthopedics"

    # Filter by specialization
    resp2 = client.post("/graphql", json={
        "query": '''
        query {
            getDoctors(specialization: "Dentistry") {
                ezId
                licenseNumber
                specialization
            }
        }
        '''
    })
    docs2 = resp2.get_json()["data"]["getDoctors"]
    assert len(docs2) == 1 and docs2[0]["licenseNumber"] == "LIC202"

# ================== ADD DOCTOR ===================

def test_add_doctor_success(client):
    _, ez_id = register_user_and_get_ezid(client, "301", 1)
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Male",
                dob: "1988-12-12T00:00:00",
                address: "Clinic Street",
                pincode: "987654",
                alternatePhoneNum: "1010101010",
                licenseNumber: "LIC301",
                specialization: "Dermatology",
                qualification: "{{\\"degree\\": \\"MD\\"}}",
                experience: 7,
                workingHours: "10am-2pm",
                appointmentWindow: 30
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["addDoctor"]
    assert data["status"] == 201
    assert "success" in data["message"].lower()

def test_add_doctor_duplicate_ezid(client):
    _, ez_id = register_user_and_get_ezid(client, "401", 1)
    mutation = f'''
    mutation {{
        addDoctor(
            ezId: "{ez_id}",
            gender: "Male",
            licenseNumber: "LIC401"
        ) {{
            status
            message
        }}
    }}
    '''
    res1 = client.post("/graphql", json={"query": mutation})
    assert res1.get_json()["data"]["addDoctor"]["status"] == 201
    # Try again with same ez_id
    res2 = client.post("/graphql", json={"query": mutation})
    data2 = res2.get_json()["data"]["addDoctor"]
    assert data2["status"] == 0
    assert "already exists" in data2["message"].lower()

def test_add_doctor_duplicate_license(client):
    # Two different users, same license
    _, ez_id1 = register_user_and_get_ezid(client, "501", 1)
    _, ez_id2 = register_user_and_get_ezid(client, "502", 1)
    license_num = "LIC500"

    mutation1 = f'''
    mutation {{
        addDoctor(
            ezId: "{ez_id1}",
            gender: "Male",
            licenseNumber: "{license_num}"
        ) {{
            status
            message
        }}
    }}
    '''
    mutation2 = f'''
    mutation {{
        addDoctor(
            ezId: "{ez_id2}",
            gender: "Female",
            licenseNumber: "{license_num}"
        ) {{
            status
            message
        }}
    }}
    '''
    assert client.post("/graphql", json={"query": mutation1}).get_json()["data"]["addDoctor"]["status"] == 201
    res2 = client.post("/graphql", json={"query": mutation2})
    data2 = res2.get_json()["data"]["addDoctor"]
    assert data2["status"] == 0
    assert "already exists" in data2["message"].lower()

def test_add_doctor_user_not_found(client):
    fake_ez_id = "ez-fake-9999-9999"
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{fake_ez_id}",
                gender: "Male",
                licenseNumber: "LIC999"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["addDoctor"]
    assert data["status"] == 404
    assert "user not found" in data["message"].lower()

def test_add_doctor_wrong_role(client):
    # Create a user with role 0 (not a health professional)
    _, ez_id = register_user_and_get_ezid(client, "601", 0)
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Male",
                licenseNumber: "LIC601"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["addDoctor"]
    assert data["status"] == 403
    assert "not a health professional" in data["message"].lower()

def test_add_doctor_missing_required_fields(client):
    # license_number required
    _, ez_id = register_user_and_get_ezid(client, "701", 1)
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Other"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()
    assert "errors" in data

# ============== UPDATE DOCTOR MUTATION TESTS ===============

def test_update_doctor_success(client):
    _, ez_id = register_user_and_get_ezid(client, "801", 1)
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Female",
                licenseNumber: "LIC801",
                address: "Old Address",
                experience: 3,
                consultationFee: 300.0
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert resp.get_json()["data"]["addDoctor"]["status"] == 201

    update_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateDoctor(
                docId: 1,
                address: "New Address",
                experience: 8,
                consultationFee: 900.0
            ) {
                status
                message
            }
        }
        '''
    })
    data = update_resp.get_json()["data"]["updateDoctor"]
    assert data["status"] == 200
    assert "updated successfully" in data["message"].lower()

def test_update_doctor_not_found(client):
    update_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateDoctor(
                docId: 999,
                address: "Ghost Address"
            ) {
                status
                message
            }
        }
        '''
    })
    data = update_resp.get_json()["data"]["updateDoctor"]
    assert data["status"] == 403
    assert "not found" in data["message"].lower()

def test_update_doctor_duplicate_license(client):
    # Create two doctors, update license to duplicate
    _, ez_id1 = register_user_and_get_ezid(client, "901", 1)
    _, ez_id2 = register_user_and_get_ezid(client, "902", 1)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id1}",
                gender: "Male",
                licenseNumber: "LIC901"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id2}",
                gender: "Female",
                licenseNumber: "LIC902"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    # Try to update doc2's license to doc1's license
    update_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateDoctor(
                docId: 2,
                licenseNumber: "LIC901"
            ) {
                status
                message
            }
        }
        '''
    })
    data = update_resp.get_json()["data"]["updateDoctor"]
    assert data["status"] == 403
    assert "license number already exists" in data["message"].lower()

def test_update_doctor_partial_fields(client):
    _, ez_id = register_user_and_get_ezid(client, "1001", 1)
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            addDoctor(
                ezId: "{ez_id}",
                gender: "Female",
                licenseNumber: "LIC1001",
                consultationFee: 1200.0,
                workingHours: "9am-5pm"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    # Only update working hours, others unchanged
    update_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateDoctor(
                docId: 1,
                workingHours: "10am-6pm"
            ) {
                status
                message
            }
        }
        '''
    })
    data = update_resp.get_json()["data"]["updateDoctor"]
    assert data["status"] == 200
    assert "updated successfully" in data["message"].lower()

def test_update_doctor_missing_docid(client):
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            updateDoctor(
                experience: 10
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()
    assert "errors" in data
    error_msg = data["errors"][0]["message"].lower()
    assert "doc_id" in error_msg or "required" in error_msg

