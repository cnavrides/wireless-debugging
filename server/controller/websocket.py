# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
WebSocket Controller
"""

import json
import time
import controller

from bottle import route, request, abort
from geventwebsocket import WebSocketError

from parsing_lib import LogParser
from helpers import util

# Store a dictionary of string -> function
_ws_routes = {}
_web_ui_ws_connections = {}


@route('/ws')
def handle_websocket():
    """ Handle an incomming WebSocket connection.

    This function handles incomming WebSocket connections and waits for
    incoming messages from the connection. When a message is recieved, it calls
    the appropriate function.
    """

    websocket = request.environ.get('wsgi.websocket')
    if not websocket:
        abort(400, 'Expected WebSocket request.')

    _websocket_metadata = {}

    while not websocket.closed:
        try:
            message = websocket.receive()
            if message is None:
                continue

            decoded_message = json.loads(message)
            message_type = decoded_message['messageType']
            if message_type is None:
                # TODO: blow up
                pass

            _ws_routes[message_type](decoded_message, websocket,
                                     _websocket_metadata)
        except WebSocketError:
            break

    # If we have the API key, we can waste a little less time searching for the
    # WebSocket.
    ws_api_key = _websocket_metadata.get('apiKey', '')
    if (ws_api_key and ws_api_key in _web_ui_ws_connections and websocket in 
            _web_ui_ws_connections[ws_api_key]):
        _web_ui_ws_connections[ws_api_key].remove(websocket)
    # ... Otherwise we have to search everywhere to find and delete it.
    else:
        for api_key, websockets_for_api_key in _web_ui_ws_connections.items():
            if websocket in websockets_for_api_key: 
                websockets_for_api_key.remove(websocket)
                break

    for api_key, websockets in list(_web_ui_ws_connections.items()): 
        if not websockets:
            del _web_ui_ws_connections[api_key]


def ws_router(message_type):
    """ Provide a decorator for adding functions to the _ws_route dictionary.
    """

    def decorator(function):
        _ws_routes[message_type] = function

    return decorator


@ws_router('startSession')
def start_session(message, websocket, metadata):
    """ Marks the start of a logging session, and attaches metadata to the
        WebSocket receiving the raw logs.
    """

    for attribute, value in message.items():
        metadata[attribute] = value


@ws_router('logDump')
def log_dump(message, websocket, metadata):
    """ Handles Log Dumps from the Mobile API.

    When a log dump comes in from the Mobile API, this function takes the raw
    log data, parses it and sends the parsed data to all connected web clients.

    Args:
        message: The decoded JSON message from the Mobile API.
        websocket: The WebSocket connection object where the log is being
            received.
    """

    parsed_logs = LogParser.parse(message)

    api_key = metadata.get('apiKey', '')
    
    associated_websockets = ( 
        controller.user_management_interface.find_associated_websockets(api_key,
            _web_ui_ws_connections))

    for connection in associated_websockets:
        connection.send(util.serialize_to_json(parsed_logs))


@ws_router('endSession')
def end_session(message, websocket, metadata):
    # TODO: Accept an end session message and notify the database to stop adding
    #       entries to the current log.
    print("currently defunct")


@ws_router('associateUser')
def associate_user(message, websocket, metadata):
    """ Associates a Web UI WebSocket connection with a session.

    When a browser requests to be associated with a session, add the associated
    WebSocket connection to the list connections for that session.

    Args:
        message: The decoded JSON message from the Mobile API. Contains the API
            key for the user.
        websocket: The WebSocket connection object where the log is being
            received.
    """

    api_key = message['apiKey']

    _web_ui_ws_connections.setdefault(api_key, []).append(websocket)
