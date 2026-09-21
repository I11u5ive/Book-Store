import pytest

from users.forms import UserRegisterForm


pytestmark = pytest.mark.django_db


def test_register_form_valid():
    form = UserRegisterForm(
        data={
            "username": "alex",
            "email": "alex@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
    )

    assert form.is_valid()


def test_register_form_password_mismatch():
    form = UserRegisterForm(
        data={
            "username": "alex",
            "email": "alex@example.com",
            "password1": "StrongPassword123!",
            "password2": "DifferentPassword123!",
        }
    )

    assert not form.is_valid()


def test_register_form_missing_username():
    form = UserRegisterForm(
        data={
            "username": "",
            "email": "alex@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
    )

    assert not form.is_valid()


def test_register_form_missing_email():
    form = UserRegisterForm(
        data={
            "username": "alex",
            "email": "",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }
    )

    assert not form.is_valid()