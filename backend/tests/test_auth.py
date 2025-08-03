import pytest

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

# ✅ Test: Successful Registration
def test_register_success(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            register(
                email: "test@example.com",
                role: 0,
                password: "pass123",
                confirmPassword: "pass123",
                name: "Test User",
                phoneNum: "1234567890"
            ) {
                status
                message
            }
        }
        '''
    })
    data = response.get_json()["data"]["register"]
    assert data["status"] == 200
    assert "successful" in data["message"].lower()

# ❌ Test: Passwords Do Not Match
def test_register_password_mismatch(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            register(
                email: "mismatch@example.com",
                role: 1,
                password: "pass123",
                confirmPassword: "wrongpass",
                name: "Mismatch User",
                phoneNum: "0987654321"
            ) {
                status
                message
            }
        }
        '''
    })
    data = response.get_json()["data"]["register"]
    assert data["status"] == 403
    assert "passwords do not match" in data["message"].lower()

# ❌ Test: Missing Required Field (email)
def test_register_missing_email(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            register(
                role: 0,
                password: "pass123",
                confirmPassword: "pass123",
                name: "No Email",
                phoneNum: "1111111111"
            ) {
                status
                message
            }
        }
        '''
    })
    # GraphQL will throw an error here due to missing required field
    assert "errors" in response.get_json()

# ❌ Test: Invalid Role (not 0 or 1)
def test_register_invalid_role(client):
    response = client.post("/graphql", json={
        "query": '''
        mutation {
            register(
                email: "invalidrole@example.com",
                role: 3,
                password: "pass123",
                confirmPassword: "pass123",
                name: "Invalid Role",
                phoneNum: "1111111111"
            ) {
                status
                message
            }
        }
        '''
    })
    data = response.get_json()["data"]["register"]
    assert data["status"] == 402
    assert "role must be either" in data["message"].lower()

# ❌ Test: Duplicate Email Registration
def test_register_duplicate_email(client):
    mutation = '''
    mutation {
        register(
            email: "duplicate@example.com",
            role: 0,
            password: "pass123",
            confirmPassword: "pass123",
            name: "User A",
            phoneNum: "2222222222"
        ) {
            status
            message
        }
    }
    '''
    client.post("/graphql", json={"query": mutation})  # First time
    response = client.post("/graphql", json={"query": mutation})  # Duplicate
    data = response.get_json()["data"]["register"]
    assert data["status"] == 409
    assert "already exists" in data["message"].lower()

# ✅ Test: getToken with Correct ez_id
def test_get_token_with_email(client,db_user,app):
    with app.app_context():
        # Create a user and get ez_id
        email, ez_id = create_user_and_get_ezid(client, db_user, "tokenuser", 1)
    
    response = client.post("/graphql", json={
        "query": f'''
        query {{
            getToken(ezId: "{ez_id}", password: "test123") {{
                token
                message
                status
            }}
        }}
        '''
    })
    print(response.get_json())
    print(ez_id,email)
    data = response.get_json()["data"]["getToken"]
    assert data["token"] is not None

# ❌ Test: getToken with Wrong Password
def test_get_token_wrong_password(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            getToken(ezId: "EZ0001", password: "wrongpass") {
                token
                message
                status
            }
        }
        '''
    })
    data = response.get_json()["data"]["getToken"]
    assert data["token"] is None

# ❌ Test: getToken with Invalid User ID
def test_get_token_invalid_user(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            getToken(ezId: "EZ9999", password: "any") {
                token
                message
                status
            }
        }
        '''
    })
    data = response.get_json()["data"]["getToken"]
    assert data["token"] is None

# ❌ Test: getToken without ez_id or email
def test_get_token_missing_fields(client):
    response = client.post("/graphql", json={
        "query": '''
        query {
            getToken(password: "any") {
                token
                message
                status
            }
        }
        '''
    })
    data = response.get_json()["data"]["getToken"]
    assert data["token"] is None
    assert data["status"] == 404
