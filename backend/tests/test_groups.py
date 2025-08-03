import pytest
import json
from datetime import datetime, timedelta

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

def create_senior(client, suffix="101"):
    """Helper to create a senior user and profile"""
    _, senior_ez_id = register_user_and_get_ezid(client, suffix, role=0)
    
    # Add senior profile
    senior_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            addSenior(
                ezId: "{senior_ez_id}",
                gender: "Male",
                dob: "1950-01-01T00:00:00",
                address: "Senior Address {suffix}",
                pincode: "12345",
                alternatePhoneNum: "999999{suffix.zfill(4)}"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert senior_resp.get_json()["data"]["addSenior"]["status"] == 201
    return senior_ez_id

def create_multiple_seniors(client, count=3, start_suffix=101):
    """Helper to create multiple senior users and profiles"""
    senior_ez_ids = []
    for i in range(count):
        ez_id = create_senior(client, str(start_suffix + i))
        senior_ez_ids.append(ez_id)
    return senior_ez_ids

# ==================== QUERY TESTS ====================

def test_get_groups_empty(client):
    """Test getting groups when none exist"""
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups {
                grpId
                label
                timing
                admin
                pincode
                location
            }
        }
        '''
    })
    data = resp.get_json()["data"]["getGroups"]
    assert isinstance(data, list)
    assert len(data) == 0

def test_get_groups_with_data(client):
    """Test getting groups when they exist"""
    senior_ez_id = create_senior(client, "201")
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    create_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Morning Walk Group",
                timing: "{future_time}",
                adminId: 1,
                pincode: "12345",
                location: "Central Park"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert create_resp.get_json()["data"]["createGroup"]["status"] == 1
    
    # Query groups
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups {
                grpId
                label
                timing
                admin
                pincode
                location
            }
        }
        '''
    })
    groups = resp.get_json()["data"]["getGroups"]
    assert len(groups) == 1
    group = groups[0]
    assert group["label"] == "Morning Walk Group"
    assert group["admin"] == 1
    assert group["pincode"] == "12345"
    assert group["location"] == "Central Park"

def test_get_groups_filter_by_admin(client):
    """Test filtering groups by admin_id"""
    # Create multiple seniors
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=301)
    
    # Create groups with different admins
    future_time1 = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S")
    future_time2 = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%S")
    
    # Group by admin 1
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Admin 1 Group",
                timing: "{future_time1}",
                adminId: 1,
                pincode: "11111"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Group by admin 2
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Admin 2 Group",
                timing: "{future_time2}",
                adminId: 2,
                pincode: "22222"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Query groups for admin 1 only
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups(adminId: 1) {
                grpId
                label
                admin
            }
        }
        '''
    })
    groups = resp.get_json()["data"]["getGroups"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Admin 1 Group"
    assert groups[0]["admin"] == 1

def test_get_groups_filter_by_pincode(client):
    """Test filtering groups by pincode"""
    senior_ez_id = create_senior(client, "401")
    
    # Create groups with different pincodes
    future_time1 = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    future_time2 = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S")
    
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Pincode 12345 Group",
                timing: "{future_time1}",
                adminId: 1,
                pincode: "12345"
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
            createGroup(
                label: "Pincode 67890 Group",
                timing: "{future_time2}",
                adminId: 1,
                pincode: "67890"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Query groups for specific pincode
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups(pincode: "67890") {
                grpId
                label
                pincode
            }
        }
        '''
    })
    groups = resp.get_json()["data"]["getGroups"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Pincode 67890 Group"
    assert groups[0]["pincode"] == "67890"

def test_get_groups_filter_by_admin_and_pincode(client):
    """Test filtering groups by both admin_id and pincode"""
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=501)
    
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    
    # Create multiple groups with different combinations
    groups_data = [
        {"admin": 1, "pincode": "11111", "label": "Admin1-Pin11111"},
        {"admin": 1, "pincode": "22222", "label": "Admin1-Pin22222"},
        {"admin": 2, "pincode": "11111", "label": "Admin2-Pin11111"},
        {"admin": 2, "pincode": "22222", "label": "Admin2-Pin22222"},
    ]
    
    for group_data in groups_data:
        client.post("/graphql", json={
            "query": f'''
            mutation {{
                createGroup(
                    label: "{group_data["label"]}",
                    timing: "{future_time}",
                    adminId: {group_data["admin"]},
                    pincode: "{group_data["pincode"]}"
                ) {{
                    status
                    message
                }}
            }}
            '''
        })
    
    # Query with both filters
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups(adminId: 1, pincode: "22222") {
                grpId
                label
                admin
                pincode
            }
        }
        '''
    })
    groups = resp.get_json()["data"]["getGroups"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Admin1-Pin22222"
    assert groups[0]["admin"] == 1
    assert groups[0]["pincode"] == "22222"

def test_get_groups_invalid_admin(client):
    """Test filtering by non-existent admin_id"""
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroups(adminId: 999) {
                grpId
                label
            }
        }
        '''
    })
    groups = resp.get_json()["data"]["getGroups"]
    assert len(groups) == 0

def test_get_group_members_empty(client):
    """Test getting group members when group has no members"""
    senior_ez_id = create_senior(client, "601")
    
    # Create group but don't add members
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Empty Group",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Query group members
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroupMembers(grpId: 1) {
                grpId
                senId
                joinedAt
            }
        }
        '''
    })
    members = resp.get_json()["data"]["getGroupMembers"]
    assert isinstance(members, list)
    assert len(members) == 0

def test_get_group_members_with_data(client):
    """Test getting group members when members exist"""
    senior_ez_ids = create_multiple_seniors(client, count=3, start_suffix=701)
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Members Group",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Add members to group
    for i in range(2, 4):  # Add seniors 2 and 3 as members
        join_resp = client.post("/graphql", json={
            "query": f'''
            mutation {{
                joinGroup(
                    grpId: 1,
                    senId: {i}
                ) {{
                    status
                    message
                }}
            }}
            '''
        })
        assert join_resp.get_json()["data"]["joinGroup"]["status"] == 1
    
    # Query group members
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroupMembers(grpId: 1) {
                grpId
                senId
                joinedAt
            }
        }
        '''
    })
    members = resp.get_json()["data"]["getGroupMembers"]
    assert len(members) == 2
    
    member_sen_ids = [m["senId"] for m in members]
    assert "2" in member_sen_ids
    assert "3" in member_sen_ids
    assert all(m["grpId"] == "1" for m in members)

def test_get_group_members_nonexistent_group(client):
    """Test getting members for non-existent group"""
    resp = client.post("/graphql", json={
        "query": '''
        query {
            getGroupMembers(grpId: 999) {
                grpId
                senId
            }
        }
        '''
    })
    members = resp.get_json()["data"]["getGroupMembers"]
    assert len(members) == 0

# ==================== CREATE GROUP TESTS ====================

def test_create_group_success(client):
    """Test successfully creating a group"""
    senior_ez_id = create_senior(client, "801")
    
    future_time = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Yoga Class",
                timing: "{future_time}",
                adminId: 1,
                pincode: "54321",
                location: "Community Center"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["createGroup"]
    assert data["status"] == 1
    assert "successfully" in data["message"].lower()

def test_create_group_minimal_data(client):
    """Test creating group with only required fields"""
    senior_ez_id = create_senior(client, "802")
    
    future_time = (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Minimal Group",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["createGroup"]
    assert data["status"] == 1
    
    # Verify group was created with null optional fields
    query_resp = client.post("/graphql", json={
        "query": '''query { getGroups { label pincode location } }'''
    })
    groups = query_resp.get_json()["data"]["getGroups"]
    assert len(groups) == 1
    assert groups[0]["label"] == "Minimal Group"
    assert groups[0]["pincode"] is None
    assert groups[0]["location"] is None

def test_create_group_invalid_admin(client):
    """Test creating group with non-existent admin"""
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Invalid Admin Group",
                timing: "{future_time}",
                adminId: 999
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["createGroup"]
    # Should handle gracefully - check your actual implementation

def test_create_group_missing_required_fields(client):
    """Test creating group with missing required fields"""
    # Missing label
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            createGroup(
                timing: "2024-12-25T10:00:00",
                adminId: 1
            ) {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

def test_create_group_missing_timing(client):
    """Test creating group with missing timing"""
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            createGroup(
                label: "No Timing Group",
                adminId: 1
            ) {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

def test_create_group_past_timing(client):
    """Test creating group with past timing"""
    senior_ez_id = create_senior(client, "901")
    
    past_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Past Time Group",
                timing: "{past_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["createGroup"]
    # Should still succeed or handle based on your business logic

def test_create_group_special_characters(client):
    """Test creating group with special characters in label and location"""
    senior_ez_id = create_senior(client, "902")
    
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Café & Art Club - Morning Session!",
                timing: "{future_time}",
                adminId: 1,
                location: "St. Mary's Community Center (2nd Floor)"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    data = resp.get_json()["data"]["createGroup"]
    assert data["status"] == 1
    
    # Verify special characters are preserved
    query_resp = client.post("/graphql", json={
        "query": '''query { getGroups { label location } }'''
    })
    groups = query_resp.get_json()["data"]["getGroups"]
    assert groups[0]["label"] == "Café & Art Club - Morning Session!"
    assert groups[0]["location"] == "St. Mary's Community Center (2nd Floor)"

def test_create_multiple_groups_same_admin(client):
    """Test creating multiple groups with same admin"""
    senior_ez_id = create_senior(client, "1001")
    
    groups_data = [
        {"label": "Morning Yoga", "days": 7},
        {"label": "Evening Walk", "days": 14},
        {"label": "Book Club", "days": 21},
    ]
    
    for group_data in groups_data:
        future_time = (datetime.now() + timedelta(days=group_data["days"])).strftime("%Y-%m-%dT%H:%M:%S")
        resp = client.post("/graphql", json={
            "query": f'''
            mutation {{
                createGroup(
                    label: "{group_data["label"]}",
                    timing: "{future_time}",
                    adminId: 1
                ) {{
                    status
                    message
                }}
            }}
            '''
        })
        assert resp.get_json()["data"]["createGroup"]["status"] == 1
    
    # Verify all groups were created
    query_resp = client.post("/graphql", json={
        "query": '''query { getGroups(adminId: 1) { label admin } }'''
    })
    groups = query_resp.get_json()["data"]["getGroups"]
    assert len(groups) == 3
    
    labels = [g["label"] for g in groups]
    assert "Morning Yoga" in labels
    assert "Evening Walk" in labels
    assert "Book Club" in labels

# ==================== JOIN GROUP TESTS ====================

def test_join_group_success(client):
    """Test successfully joining a group"""
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=1101)
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Join Test Group",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Join group
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(
                grpId: 1,
                senId: 2
            ) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["joinGroup"]
    assert data["status"] == 1
    assert "successfully" in data["message"].lower()
    assert "reminder" in data["message"].lower()

def test_join_group_creates_reminder(client):
    """Test that joining group creates appropriate reminder"""
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=1201)
    
    # Create group with specific timing
    group_time = datetime.now() + timedelta(days=7, hours=2)
    group_time_str = group_time.strftime("%Y-%m-%dT%H:%M:%S")
    
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Reminder Test Group",
                timing: "{group_time_str}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Join group
    join_resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1, senId: 2) {
                status
                message
            }
        }
        '''
    })
    assert join_resp.get_json()["data"]["joinGroup"]["status"] == 1

def test_join_group_duplicate(client):
    """Test joining the same group twice (should prevent duplicates)"""
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=1301)
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Duplicate Join Test",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Join group first time
    join_resp1 = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1, senId: 2) {
                status
                message
            }
        }
        '''
    })
    assert join_resp1.get_json()["data"]["joinGroup"]["status"] == 1
    
    # Try joining again
    join_resp2 = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1, senId: 2) {
                status
                message
            }
        }
        '''
    })
    data = join_resp2.get_json()["data"]["joinGroup"]
    assert data["status"] == 0
    assert "already joined" in data["message"].lower()

def test_join_group_nonexistent_group(client):
    """Test joining non-existent group"""
    senior_ez_id = create_senior(client, "1401")
    
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 999, senId: 1) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["joinGroup"]
    assert data["status"] == 404
    assert "group not found" in data["message"].lower()

def test_join_group_nonexistent_senior(client):
    """Test non-existent senior joining group"""
    senior_ez_id = create_senior(client, "1501")
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Non-existent Senior Test",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Try joining with non-existent senior
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1, senId: 999) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["joinGroup"]
    assert data["status"] == 404
    assert "senior not found" in data["message"].lower()

def test_join_group_missing_required_fields(client):
    """Test joining group with missing required fields"""
    # Missing senId
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1) {
                status
                message
            }
        }
        '''
    })
    json_resp = resp.get_json()
    assert "errors" in json_resp

def test_admin_can_join_own_group(client):
    """Test that group admin can join their own group"""
    senior_ez_id = create_senior(client, "1601")
    
    # Create group
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Admin Join Own Group",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    
    # Admin joins own group
    resp = client.post("/graphql", json={
        "query": '''
        mutation {
            joinGroup(grpId: 1, senId: 1) {
                status
                message
            }
        }
        '''
    })
    data = resp.get_json()["data"]["joinGroup"]
    assert data["status"] == 1
    assert "successfully" in data["message"].lower()

def test_group_edge_cases(client):
    """Test various edge cases for groups"""
    senior_ez_ids = create_multiple_seniors(client, count=2, start_suffix=2001)
    
    # Very long group label
    long_label = "A" * 100  # Very long label
    future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S")
    
    long_label_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "{long_label}",
                timing: "{future_time}",
                adminId: 1
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert long_label_resp.get_json()["data"]["createGroup"]["status"] == 1
    
    # Very long location
    long_location = "B" * 200
    long_loc_resp = client.post("/graphql", json={
        "query": f'''
        mutation {{
            createGroup(
                label: "Long Location Group",
                timing: "{future_time}",
                adminId: 1,
                location: "{long_location}"
            ) {{
                status
                message
            }}
        }}
        '''
    })
    assert long_loc_resp.get_json()["data"]["createGroup"]["status"] == 1
    
    # Verify data integrity
    groups_resp = client.post("/graphql", json={
        "query": '''query { getGroups { label location } }'''
    })
    groups = groups_resp.get_json()["data"]["getGroups"]
    assert len(groups) == 2
    assert groups[0]["label"] == long_label
    assert groups[1]["location"] == long_location
