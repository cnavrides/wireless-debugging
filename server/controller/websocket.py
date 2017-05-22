"""
WebSocket Controller
"""

import json
import time

from bottle import route, request, abort

from geventwebsocket import WebSocketError

# Store a dictionary of string -> function
_ws_routes = {}
_web_interface_ws_connections = []


@route('/ws')
def handle_websocket():
    """ Handle an incomming WebSocket connection.

    This function handles incomming WebSocket connections and waits for
    incomming messages from the connection. When a message is recieved, it
    calls the appropriate function.
    """

    websocket = request.environ.get('wsgi.websocket')
    if not websocket:
        abort(400, 'Expected WebSocket request.')

    while not websocket.closed:
        try:
            message = websocket.receive()
            if message is None:
                continue

            decoded_message = json.loads(message)
            messageType = decoded_message['messageType']
            if messageType is None:
                # TODO: blow up
                pass

            _ws_routes[messageType](decoded_message, websocket)
        except WebSocketError:
            break

    # Remove the WebSocket connection from the list once it is closed
    _web_interface_ws_connections.remove(websocket)


def ws_router(messageType):
    """ Provide a decorator for adding functions to the _ws_route dictionary """
    def decorator(function):
        _ws_routes[messageType] = function

    return decorator


@ws_router('logDump')
def logDump(message, websocket):
    """ Handles Log Dumps from the Mobile API

    When a log dump comes in from the Mobile API, this function takes the raw
    log data, parses it and sends the parsed data to all connected web clients.

    Args:
        message: the decoded JSON message from the Mobile API
        websocket: the full websocket connection
    """
    # TODO: This function is entirely a placeholder for testing purposes
    parsed_logs = json.dumps({
        'messageType': 'logData',
        'osType': 'Android',
        'logEntries': [
            {
                'time': '2017-11-06T16:34:41.000Z',
                'text': 'This is not a real error',
                'tag': 'TEST',
                'logType': 'Warning',
            },
            {
                'time': '2017-11-06T16:34:50.000Z',
                'text': 'Cool Log',
                'tag': 'TEST',
                'logType': 'Info',
            },
            {
                'time': '2017-11-06T16:34:55.000Z',
                'text': 'Cool Log',
                'tag': 'TEST',
                'logType': 'Error',
            },
        ]
    })

    for c in _web_interface_ws_connections:
        c.send(parsed_logs)
        time.sleep(1)
        c.send(parsed_logs)


@ws_router('associateSession')
def associateSession(message, websocket):
    """ Associates a WebSocket connection with a session

    When a browser requests to be associated with a session, add the associated
    WebSocket connection to the list connections for that session.

    Args:
        message: the decoded JSON message from the Mobile API
        websocket: the full websocket connection
    """

    # TODO: Currently we only have one session, when we implement multiple
    #       connections, modify this to handle it
    _web_interface_ws_connections.append(websocket)
