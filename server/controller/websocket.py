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
# TODO: Reverse map to go API key -> websocket, rather than websocket -> API key
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

    print('connection received')

    while not websocket.closed:
        try:
            message = websocket.receive()
            if message is None:
                continue

            decoded_message = json.loads(message)
            print(decoded_message)
            message_type = decoded_message['messageType']
            if message_type is None:
                # TODO: blow up
                pass

            _ws_routes[message_type](decoded_message, websocket,
                                     _websocket_metadata)
        except WebSocketError:
            break

    # If we have the api key, we can waste a little less time searching for the
    # websocket.
    if _websocket_metadata.get('apiKey', ''):
        _web_ui_ws_connections[_websocket_metadata['apiKey']].remove(websocket)
    # ... Otherwise we have to search everywhere to find and delete it.
    else:
        for api_key, websockets in _web_ui_ws_connections.items():
            if websocket in websockets: 
                websockets.remove(websocket)
                break

    for api_key in list(_web_ui_ws_connections):
        if not _web_ui_ws_connections[api_key]:
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
        websocket receiving the raw logs.
    """

    # There's probably a better way to do this and it should be refactored.
    for attribute, value in message.items():
        metadata[attribute] = value


@ws_router('logDump')
def log_dump(message, websocket, metadata):
    """ Handles Log Dumps from the Mobile API.

    When a log dump comes in from the Mobile API, this function takes the raw
    log data, parses it and sends the parsed data to all connected web clients.

    Args:
        message: The decoded JSON message from the Mobile API.
        websocket: The websocket connection object where the log is being
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
        message: The decoded JSON message from the Mobile API. Contains the api
            key for the user.
        websocket: The websocket connection object where the log is being
            received.
    """

    if not _web_ui_ws_connections.get(message['apiKey'], ''):
        _web_ui_ws_connections[message['apiKey']] = []

    _web_ui_ws_connections.get(message['apiKey'], '').append(websocket)
