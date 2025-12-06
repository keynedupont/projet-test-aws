import pytest
from pydantic import ValidationError
from projet.auth.schemas import UserCreate


def test_user_create_valid_password():
    u = UserCreate(email="user@test.com", password="Test123!")
    assert u.email == "user@test.com"


def test_user_create_invalid_password_no_digit():
    with pytest.raises(ValidationError):
        UserCreate(email="user@test.com", password="Test!!!!")
