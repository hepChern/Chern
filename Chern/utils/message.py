"""
Created by Mingrui Zhao @ 2025
define the messages class
"""

from .pretty import colorize

class Message:
    """ A class to define messages used in the project,
    the message is a list with tuple (text, type), for different typing purpose
    """

    def __init__(self):
        self.messages = []

    def add(self, text, msg_type=""):
        """ Add a message to the list
        """
        self.messages.append((text, msg_type))

    def __str__(self):
        """ String representation of the messages
        """
        return "".join(f"{msg_type}: {text}" for text, msg_type in self.messages)

    def colored(self):
        """ Return colored messages
        """
        return "".join(colorize(text, msg_type) for text, msg_type in self.messages)
