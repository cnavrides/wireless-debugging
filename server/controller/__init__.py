"""
Controller Module
"""

import controller.root
import controller.sessions
import controller.websocket

# Replace MongoDataStoreInterface with your desired datastore interface.
from datastore_interfaces.mongo_datastore_interface import MongoDatastoreInterface

# Replace email_auth with your desired user management interface
from user_management_interfaces import email_auth

# This needs to be accessed by root and websockets, so it's being kept one level
# above.
# Also replace email_auth.EmailAuth() with your desired user management
# interface.
# Also replace MongoDataStoreInterface() with your desired datastore interface.
user_management_interface = email_auth.EmailAuth()
datastore_interface = MongoDatastoreInterface()
