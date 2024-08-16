# tests/test_users.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import Base, get_db
from app.schema import UserCreate
from app.auth import create_access_token
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure tables are created before tests
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Fixture to create a test user
@pytest.fixture(scope="module")
def test_user():
    user_data = {"username": "testuser", "password": "testpassword",}
    response = client.post("/users/", json=user_data)
    if response.status_code != 200:
        logger.error(f"Error creating test user: {response.json()}")
    else:
        logger.info(f"Test user created successfully: {response.json()}")
    return response.json()

# Test case to create a user
def test_create_user():
    user_data = {"username": "unique_user", "password": "newpassword", "email": "uniqueuser@example.com"}
    response = client.post("/users/", json=user_data)
    if response.status_code != 200:
        logger.error(f"Error creating user: {response.json()}")
    else:
        logger.info(f"User created successfully: {response.json()}")
    assert response.status_code == 200
    assert response.json()["username"] == "unique_user"

# Test case to handle duplicate username
def test_create_user_duplicate():
    user_data = {"username": "testuser", "password": "testpassword","email": "testuser@example.com"}
    response = client.post("/users/", json=user_data)
    if response.status_code != 400:
        logger.error(f"Error handling duplicate username: {response.json()}")
    else:
        logger.info(f"Duplicate username handled correctly: {response.json()}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

# Test case for user login
def test_login_for_access_token():
    login_data = {"username": "testuser", "password": "testpassword", "email": "testuser@example.com"}
    response = client.post("/users/token", data=login_data)
    if response.status_code != 200:
        logger.error(f"Error logging in: {response.json()}")
    else:
        logger.info(f"Login successful: {response.json()}")
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

# Test case to get current user
def test_read_users_me(test_user):
    token = test_login_for_access_token()
    if not token:
        logger.error("No access token found in test_user response.")
        pytest.fail("No access token found in test_user response.")
    
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me/", headers=headers)
    if response.status_code != 200:
        logger.error(f"Error getting user info: {response.json()}")
    else:
        logger.info(f"User info retrieved successfully: {response.json()}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

