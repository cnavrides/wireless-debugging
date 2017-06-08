"""
A websocket placeholder class for testing.
"""

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
