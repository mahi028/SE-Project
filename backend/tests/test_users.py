import pytest

# ✅ Test: Add a user successfully
def test_add_user_success(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            addUser(
                ezId: "U001",
                role: "0",
                email: "testuser@example.com",
                password: "secret",
                name: "Test User",
                gender: "Male",
                age: 25,
                phoneNum: "1234567890",
                profileImageUrl: "http://example.com/image.jpg"
            ) {
                status
                message
            }
        }
        '''
    })

    data = response.get_json()["data"]["addUser"]
    assert data["status"] == 201
    assert "success" in data["message"].lower()


# ❌ Test: Add user with duplicate email or ez_id (should fail)
def test_add_user_duplicate(client):
    mutation = '''
    mutation {
        addUser(
            ezId: "U002",
            role: "1",
            email: "duplicate@example.com",
            password: "secret",
            name: "First",
            gender: "Female",
            age: 30,
            phoneNum: "9999999999",
            profileImageUrl: ""
        ) {
            status
            message
        }
    }
    '''
    # First insert
    client.post("/graphql", json={"query": mutation})
    # Duplicate insert
    response = client.post("/graphql", json={"query": mutation})
    data = response.get_json()["data"]["addUser"]
    assert data["status"] == 500
    assert "failure" in data["message"].lower()


# ✅ Test: Fetch all users (should return correct number)
def test_all_users(client):
    # Add 2 users
    for i in range(2):
        client.post("/graphql", json={
            "query": f'''
            mutation {{
                addUser(
                    ezId: "U00{i+10}",
                    role: "1",
                    email: "user{i}@test.com",
                    password: "pw{i}",
                    name: "User {i}",
                    gender: "Other",
                    age: 20,
                    phoneNum: "00000{i}",
                    profileImageUrl: ""
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
            allUsers {
                ezId
                email
                name
            }
        }
        '''
    })

    data = response.get_json()["data"]["allUsers"]
    assert isinstance(data, list)
    assert len(data) >= 2  # Because some other tests also insert


# ✅ Test: Fetch user by ez_id
def test_get_user_by_ez_id(client):
    # Insert user first
    client.post("/graphql", json={
        "query": '''
        mutation {
            addUser(
                ezId: "U050",
                role: "1",
                email: "eziduser@example.com",
                password: "pass",
                name: "EZ User",
                gender: "Male",
                age: 40,
                phoneNum: "7777777777",
                profileImageUrl: ""
            ) {
                status
                message
            }
        }
        '''
    })

    response = client.post("/graphql", json={
        "query": '''
        query {
            user(ezId: 50) {
                ezId
                email
                name
            }
        }
        '''
    })

    data = response.get_json()["data"]["user"]
    assert data["email"] == "eziduser@example.com"


# ✅ Test: Fetch user by email
def test_get_user_by_email(client):
    # Insert user
    client.post("/graphql", json={
        "query": '''
        mutation {
            addUser(
                ezId: "U060",
                role: "0",
                email: "byemail@example.com",
                password: "pass",
                name: "Email User",
                gender: "F",
                age: 28,
                phoneNum: "1231231234",
                profileImageUrl: ""
            ) {
                status
                message
            }
        }
        '''
    })

    response = client.post("/graphql", json={
        "query": '''
        query {
            user(email: "byemail@example.com") {
                ezId
                email
                name
            }
        }
        '''
    })

    data = response.get_json()["data"]["user"]
    assert data["ezId"] == "U060"
    assert data["name"] == "Email User"


# ❌ Test: Fetch user with invalid ez_id and email (should return null)
def test_get_user_invalid(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            user(ezId: 9999) {
                email
                name
            }
        }
        '''
    })
    data = response.get_json()["data"]["user"]
    assert data is None
