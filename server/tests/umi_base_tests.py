"""
Tests the base user management interface class. This is an abstract class so it 
just verifies that everything is unimplemented.

These tests are pretty trivial.
"""

import pytest

from user_management_interfaces import user_management_interface_base
from bottle import request, response

def test_get_login():
    """ Checks if the function is not implemented. """
    umi = user_management_interface_base.UserManagementInterfaceBase()
    base_url = "http://0.0.0.0:80"
    with pytest.raises(NotImplementedError):
        umi.get_login_ui(base_url)


def test_user_logged_in():
    """ Checks if the function is not implemented. """
    umi = user_management_interface_base.UserManagementInterfaceBase()
    with pytest.raises(NotImplementedError):
        umi.is_user_logged_in(request)


def test_handle_login():
    """ Checks if the function is not implemented. """
    umi = user_management_interface_base.UserManagementInterfaceBase()
    with pytest.raises(NotImplementedError):
        umi.handle_login("", request, response)


def test_get_api_key():
    """ Checks if the function is not implemented. """
    umi = user_management_interface_base.UserManagementInterfaceBase()
    with pytest.raises(NotImplementedError):
        umi.get_api_key_for_user(request)


def test_find_websockets():
    """ Checks if the function is not implemented. """
    umi = user_management_interface_base.UserManagementInterfaceBase()
    with pytest.raises(NotImplementedError):
        umi.find_associated_websockets("", "")
