from .conversation import Conversation
from .history import History
from .state import State


class ContextEngine:

    def __init__(self):

        self.conversation = Conversation()
        self.history = History()
        self.state = State()

    def remember_conversation(self, speaker, text):

        self.conversation.add(speaker, text)

    def remember_command(self, command):

        self.history.add(command)

    def update_state(self, key, value):

        self.state.set(key, value)

    def get_state(self, key):

        return self.state.get(key)

    def reset(self):
        self.conversation.clear()
        self.history.clear()
        self.state.clear()