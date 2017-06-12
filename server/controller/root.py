# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Root Controller
"""

from bottle import abort, post, redirect, request, response, route, static_file
from helpers.util import from_config_yaml
from kajiki_view import kajiki_view
from markupsafe import Markup

import controller

@route('/')
@kajiki_view('index')
def index():
    """ The log streaming dashboard, this is where logs go when they're
        streamed.
    
    Checks if the user is logged in. If not, redirects them to a login page.
    Otherwise sends them to the log viewing dashboard, where the logs are 
    streamed to.

    Args:
        None
    Returns:
        If the user is not logged in, redirects them to the login page.
        Otherwise this returns a webpage specified in the kajiki view decorator
        with the additional values in a dictionary.
        page: The page that Kajiki should show.
        api_key: The Web UI user's API key. 

    """

    if not controller.user_management_interface.is_user_logged_in(request):
        redirect('/login_page')

    api_key = controller.user_management_interface.get_api_key_for_user(request)

    return {
        'page': 'index', 
        'api_key': api_key,
        # If you've made it here, you have to be successfully logged in
        'logged_in': True,
    }


@route('/resources/<filepath:path>')
def static(filepath):
    """
    Routes all of the resources
    http://stackoverflow.com/a/13258941/2319844
    """
    return static_file(filepath, root='resources')


@route('/login_page')
@kajiki_view('login')
def login():
    """ Retrieves the login page from the user management interface and serves
        it to the user.

    Args:
        None
    Returns:
        An HTML webpage containing a UI for the user to log into the website.
        This function returns a webpage specified by the kajiki view decorator. 
        This function also returns a subcomponent of a webpage that defines the
        format of the login page, which is specified in the user management 
        interface. 
    """
    
    return {
        'login_fields': Markup(
            controller.user_management_interface.get_login_ui()),
        'logged_in': controller.user_management_interface.is_user_logged_in(
            request),
    }

@post('/login')
def handle_login():
    """ Takes a login form and verifies the user's identity. """
    login_successful, error_message = (
        controller.user_management_interface.handle_login(request.forms,
                                                          request, response))

    # If handle_login returned a string, it means it failed and returned an 
    # error message.
    if not login_successful:
        # TODO: Make better error handling
        print("Something went wrong!:", error_message)
        abort(403, "Login failed, error: %s" % error_message)
    else:
        redirect('/')

@route('/logout')
def logout():
    """ Logs the user out of the web UI interface.

    Functionally this just takes the API key cookie on the user's machine and
    sets it to a dummy value and expires it immediately.

    Uses the bottle response object, which can modify cookies on a user's
    browser. 

    Returns a modified, expried cookie on the user's browser.
    Also redirects to this website's index page, which should redirect to
    the login page.
    """

    response.set_cookie("api_key", "", expires=0)
    redirect('/')