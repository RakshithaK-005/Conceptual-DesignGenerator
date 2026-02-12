import pytest
from fastapi import status


@pytest.mark.asyncio
class TestAuthentication:
    """Authentication endpoint tests"""

    async def test_register_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == test_user_data["email"]

    async def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email"""
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login_success(self, client, test_user_data):
        """Test successful login"""
        client.post("/auth/register", json=test_user_data)
        
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

    async def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        client.post("/auth/register", json=test_user_data)
        
        login_data = {
            "email": test_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestUsers:
    """User endpoint tests"""

    async def test_get_current_user(self, client, test_user_data):
        """Test getting current user profile"""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Get user profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == test_user_data["email"]

    async def test_update_user_profile(self, client, test_user_data):
        """Test updating user profile"""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_response = client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        token = login_response.json()["access_token"]
        
        # Update profile
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"full_name": "Updated Name"}
        response = client.put("/users/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "Updated Name"
