# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Controller Module
"""

import controller.root
import controller.sessions
import controller.websocket

# Replace email_auth with your desired user management interface
from user_management_interfaces import email_auth

# This needs to be accessed by root and websockets, so it's being kept one level
# above.
# Also replace email_auth.EmailAuth() with your desired user management
# interface.
user_management_interface = email_auth.EmailAuth()
