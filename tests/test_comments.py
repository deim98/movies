# tests/test_comments.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from app.database import Base, get_db
import logging

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



Base.metadata.create_all(bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# Fixture to create a test user
@pytest.fixture(scope="function")
def test_user(client):
    user_data = {"username": "testuser", "password": "testpassword", "email": "testuser@example.com"}
    
    response = client.post("/signup", json=user_data)
    logger.info(f"Signup response: {response.status_code}, {response.json()}")

    if response.status_code == 400 and response.json().get("detail") == "Username already registered":
        # If the user already exists, attempt to log in and retrieve the token
        login_data = {"username": user_data["username"], "password": user_data["password"]}
        logger.info(f"Login data: {login_data}")
        response = client.post("/login", data=login_data)  # Use 'data' instead of 'json' for form data
        logger.info(f"Login response: {response.status_code}, {response.json()}")
        
        if response.status_code != 200:
            pytest.fail(f"Failed to log in with existing user: {response.json()}")
        return response.json()  # Return the login response (including the token)
    
    elif response.status_code != 200:
        logger.error(f"Error creating user: {response.json()}")
        pytest.fail(f"Failed to create test user: {response.json()}")
    
    return response.json()  # Return the signup response (including the token)

# Fixture to create a test movie
@pytest.fixture(scope="function")
def test_movie(client, test_user):
    movie_data = {"title": "Test Movie", "description": "Test Description"}
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    response = client.post("/movies/", json=movie_data, headers=headers)
    logger.info(f"Movie creation response: {response.status_code}")
    assert response.status_code == 200
    return response.json()

    
def test_create_and_read_comments(client, test_user, test_movie):
    # Create a comment first
    comment_data = {"content": "This is a test comment","movie_id": test_movie['id']}
    headers = {"Authorization": f"Bearer {test_user['access_token']}"}
    
    logger.info(f"Creating a comment for movie ID {test_movie['id']}")
    create_response = client.post(f"/movies/{test_movie['id']}/comments", json=comment_data, headers=headers)
    logger.info(f"Comment creation response: {create_response.status_code}, {create_response.json()}")
    
    assert create_response.status_code == 200
    
    
    # Now read the comments
    logger.info(f"Reading comments for movie ID {test_movie['id']}")
    read_response = client.get(f"/comments/{test_movie['id']}/", headers=headers)
    logger.info(f"Read comments response: {read_response.status_code}, {read_response.json()}")
    
    assert read_response.status_code == 200
    comments = read_response.json()
    assert isinstance(comments, list)
    assert len(comments) > 0  # Ensure that the list is not empty
    
    # Check if the created comment is in the list
    assert any(comment["content"] == "This is a test comment" for comment in comments), "The created comment was not found in the list."
