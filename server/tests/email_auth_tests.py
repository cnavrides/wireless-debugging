"""
Tests the email authorization implementationo of the user management interface.
"""

import os

from user_management_interfaces import email_auth
from bottle import request, response

def test_get_login():
    """ Verify that the login UI is read from fie and returned properly.

        This test needs to run from the server folder so that the pathing is
        consistent.
    """
    umi = email_auth.EmailAuth()
    base_url = 'http://0.0.0.0:80'

    # Ugly format because we can't have any changes in whitespace so that the 
    # test works properly.
    target = '''<form action="/login" method="post" accept-charset="UTF-8" class="form-horizontal">
    <div class="form-group">
        <label class="col-sm-2 control-label">Email:</label>
        <div class="col-sm-10">
            <input class="form-control" type="text" name="username" placeholder="Enter your email here..."/>
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-10 col-sm-offset-2">
            <button type="submit" class="btn btn-default">Submit</button>
        </div>
    </div>
</form>'''

    assert umi.get_login_ui(base_url) == target


def test_exists_in_table():
    """ Tests that the checking if a user or an api key exists in the table
        works. Also verifies that if they don't exist that this function returns
        false. This is higher up because later functions rely on 
        exists_in_table().
    """
    umi = email_auth.EmailAuth()
    umi.user_key_table = 'temp_file.txt'

    test_username = 'hi@gmail.com'

    assert not umi.exists_in_table(test_username, True)
    assert not umi.exists_in_table(test_username, False)

    user_table = open('temp_file.txt', 'w')
    user_table.write('%s,%s\n' % (test_username, test_username))
    user_table.close()

    assert umi.exists_in_table(test_username, True)
    assert umi.exists_in_table(test_username, False)

    os.remove(umi.user_key_table)


def test_user_not_logged_in():
    """ Verify that if the api cookie is not in the user's browswer that the
        login check returns false.
    """
    umi = email_auth.EmailAuth()
    assert not umi.is_user_logged_in(request)


'''
# This test needs to be fixed since it relies on cookies
def test_user_logged_in():
    """ Verify that if the api cookie is is in the user's browser that the login
        check returns true.
    """
    umi = email_auth.EmailAuth()
    request.set_cookie('api_key', 'hello_world')

    assert request.get_cookie('api_key') is not None
    assert not umi.is_user_logged_in(request)
'''


class dummyForm:
    """ A placeholder form that gets inserted into the handle_login function.
    """
    
    def __init__(self):
        self.form_data = {
            'username': 'test@test.com',
        }

    def get(self, item_name):
        """ Grabs a value from form data. """
        return self.form_data.get(item_name)


def test_handle_new_login():
    """ Verify that when a new user logs in they'll be added to the user-api key
        table, and verify that they successfully log in.
    """
    umi = email_auth.EmailAuth()
    # It'd be nice to actualy make this a temp file.
    umi.user_key_table = 'temp_file.txt' 

    form = dummyForm()
    result = umi.handle_login(form, request, response)

    assert result == (True, 'New user! Adding to users table.')

    os.remove(umi.user_key_table)


def test_handle_returning_login():
    """ Verify that when a user returns and logs in again, they are accepted
        without any diagnostic messages.
    """
    umi = email_auth.EmailAuth()
    # It'd be nice to actualy make this a temp file.
    umi.user_key_table = 'temp_file.txt'

    test_username = 'test@test.com'

    user_table = open('temp_file.txt', 'w')
    user_table.write('%s,%s\n' % (test_username, test_username))
    user_table.close()

    form = dummyForm()
    result = umi.handle_login(form, request, response)

    assert result == (True, '')

    os.remove(umi.user_key_table)

def test_get_api_key():
    """ Verify that given an existing username, the corresponding api key is
        returned.
    """
    umi = email_auth.EmailAuth()
    # It'd be nice to actualy make this a temp file
    umi.user_key_table = 'temp_file.txt'

    test_username = 'test@test.com'
    test_api_key = 'TestAPIKEY'

    user_table = open('temp_file.txt', 'w')
    user_table.write('%s,%s\n' % (test_username, test_api_key))
    user_table.close()

    assert umi.get_api_key_for_user(request) == test_api_key

    os.remove(umi.user_key_table)


def test_find_websockets():
    """ Verify that given an API key and a set of websocket connections, a list
        of websocket connections corresponding to the API key are returned.
    """

    umi = email_auth.EmailAuth()

    assert False