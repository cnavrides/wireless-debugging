"""
A simple form of 'authorization' where the user enters their email. 
THIS IS NOT A SECURE METHOD OF AUTHORIZATION. This just enables a server to
direct log files to specific machines, rather than having the logs be broadcast
to all web UI websockets.
"""

import os.path

from user_management_interfaces import user_management_interface_base

class EmailAuth(user_management_interface_base.UserManagementInterfaceBase):
    """ A User Management Interface that uses emails to direct logs to
        the appropriate Web UI.
    """

    def __init__(self):
        self.user_key_table = 'key_table.txt'
        self.login_fields_path = 'user_management_interfaces/email_login.xhtml'

    def get_login_ui(self, base_url):
        """ Returns XHTML containing a login form. 

        Args:
            class members:
                login_fields_path: String, contains the path to the file that 
                    contains the XHTML.
        Returns:
            An XHTML page containing the login form.
        """
        login_fields_file = open(self.login_fields_path, 'r')
        login_fields = login_fields_file.read()
        login_fields_file.close()

        return login_fields

    def is_user_logged_in(self, request):
        """ If a stashed cookie is found indicating that the user has logged in,
            return true. Otherwise return false.

        Args:
            request: A Bottle request object. Used to retrive cookies from the 
                user's browser.
        Returns:
            A boolean, returns true if the cookie is found and the cookie is
            legitimate. False otherwise.
        """

        # Check if the user's already logged in,
        if request.get_cookie('api_key'):
            # ... and that the api key they have is valid.
            api_key = request.get_cookie('api_key')
            print(api_key)
            if self.exists_in_table(api_key, False):
                return True
            
        return False

    def handle_login(self, form_data, request, response):
        """ Checks if the user is in the user to api key table. If they are
            returns true. If not adds the user to the table and returns true
            with an additional message.

        Args:
            form_data: The form data from the ('/login') post from bottle. Only
                contains a 'username' field where the user's email is supposed
                to go, though it doesn't explicitly have to be a user's email.
            request: A bottle request object. Used to get the api_key for the
                user.
            response: A bottle response object. Used to manipulate cookies on
                the user's browser.
        Returns:
            A tuple containing:
                login_successful: Boolean, returns true if the login was
                    successful. Returns false otherwise.
                error_message: String, returns a message describing why the 
                    login failed if login_successful is false. If 
                    login_successful is true, this can return either a blank
                    string or log message to describe anything important.
            Also sets a cookie in the user's browser containing their api key.
        """

        user_email = form_data.get('username')

        if self.exists_in_table(user_email, True):
            response.set_cookie('api_key', 
                                self.get_api_key_for_user(request))
            return (True, '')
        else:
            user_key_file = open(self.user_key_table, 'a')
            user_key_file.write(user_email + ',' + user_email + '\n')
            user_key_file.close()

            # This should be a trivial test since we just added the entry, but
            # just in case.
            if self.exists_in_table(user_email, True):
                response.set_cookie('api_key', 
                                    self.get_api_key_for_user(request))
                return (True, 'New user! Adding to users table.')

        return (False, 'Failed to login! User does not exist in table!')


    def get_api_key_for_user(self, request):
        """ Gets the API key for the user.

        Args:
            request: A bottle request object. Used to retrieve cookies. 
                Specifically retrives the 'api_key' cookie.
        Returns:
            A string, containing the api key for the user.
        """

        user_key_table = self.get_table()

        """ The less cool version of what's below
        api_key_cookie = request.get_cookie('api_key')
        if api_key_cookie and self.exists_in_table(
            request.get_cookie('api_key', False)):
            return api_key_cookie

        user_list = [table_row[0] for table_row in user_key_table]
        row_index = user_list.index(request.forms.get('username'))
        return user_key_table[row_index][1]
        """

        # This should probably be refactored, but it's pretty awesome
        # ... and terrifying
        return (request.get_cookie('api_key') if request.get_cookie('api_key') 
                and self.exists_in_table(request.get_cookie('api_key'), False) 
                else user_key_table[
                    [table_row[0] for table_row in user_key_table].index(
                        request.forms.get('username'))][1])

    def find_associated_websockets(self, api_key, websocket_connections):
        """ Returns a list of websockets that correspond to the given api key.

        Args:
            api_key: String, contains an api_key that identifies a user.
            websocket_connections: A dictionary of api keys -> lists of
                websockets.
        Returns:
            A list of websockets corresponding to the api key. If there is no
            key in the dictionary that corresponds to the given api_key, returns
            and empty list.
        """
        return websocket_connections.get(api_key, [])

    def get_table(self):
        """ Returns the table of users to api keys as a list of tuples. 
    
        Args:
            class members:
                user_key_table: String, the path to the user to api key table.
        Returns:
            None if the file doesn't exist.
            A list of tuples containing the table of users to api keys
            otherwise.
        """

        # If the table doesn't exist yet, then they can't exist in the table.
        if not os.path.isfile(self.user_key_table):
            return None

        with open(self.user_key_table, 'r') as user_key_file:    
            # Splits each row of the file by comma, yielding an email and an api
            # key.
            user_key_table = [(line.split(',')[0], line.split(',')[1]) 
                              for line in user_key_file.read().splitlines()]

        return user_key_table

    def exists_in_table(self, user_key, is_user):
        """ Checks if a given API key or user exists in the user to api key
            table.

        Args:
            user_key: The key to verify in the table. This can either be an API 
                      key or a user email.
            is_user: Boolean, if this is true, then a user email was passed in,
                              if this is false, then an api key was passed in.
        Returns:
            Boolean, true if the key existed in the table, false otherwise.
        """

        user_key_table = self.get_table()
        if not user_key_table:
            return False

        # 0 is for users, 1 is for api keys
        check_index = 0 if is_user else 1

        if any(user_key == key[check_index] for key in user_key_table):
            return True

        return False
