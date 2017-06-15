"""
Tests components of the WebSocket controller.
"""

from controller import websocket
from tests.test_classes import DummySocket


def test_start_session():
    """ Verifies that start session passes all of data from message into
        metadata where it can be stored for the lifetime of the WebSocket.
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

    # Just ensure that the start time was added, since it is set to
    # datetime.now, we can't do a full comparison.
    assert 'startTime' in _metadata
    _metadata.pop('startTime')

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

    assert message['apiKey'] in websocket._web_ui_ws_connections
    assert socket in websocket._web_ui_ws_connections[message['apiKey']]
