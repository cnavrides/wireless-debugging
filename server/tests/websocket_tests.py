"""
Tests components of the websocket controller.
"""

from controller import websocket


class DummySocket:
    """ A dummy websocket class.

        Acts as a placeholder for websockets for functions that require
        websockets. Contains the necessary methods, but provides no actual
        websocket functionality. 
    """

    def __init__(self):
        self.sent_messages = []

    def send(self, message):
        """ Tracks the messages sent by send message. """
        self.sent_messages.append(message)

    def receive(self):
        return {
            "messageType": "startSession",
            "apiKey": "f983kDduxhnJDKI22D2Kda",
            "osType": "Android",
            "deviceName": "Google Pixel",
            "appName": "Google Hangouts"
        }


def test_start_session():
    """ Verifies that start session passes all of data from message into
        metadata where it can be stored for the lifetime of the websocket.
    """
    socket = DummySocket()
    _metadata = {}
    message = {
        "messageType": "startSession",
        "apiKey": "f983kDduxhnJDKI22D2Kda",
        "osType": "Android",
        "deviceName": "Google Pixel",
        "appName": "Google Hangouts"
    }

    websocket._ws_routes[message['messageType']](message, socket, _metadata)
    assert message == _metadata


def test_associate_user():
    """ Verifies that when a user connects the server on a web UI their 
        connection is tied to some metadata stored in a private array,
        specifically their API key.
    """
    socket = DummySocket()
    _metadata = {}
    message = {
        "messageType": "associateUser",
        "apiKey": "cb572446-21f2-44d0-8983-4cf30300b574"
    }

    websocket._ws_routes[message['messageType']](message, socket, _metadata)

    assert socket in websocket._web_interface_ws_connections
    assert websocket._web_interface_ws_connections[socket] == message['apiKey']
    