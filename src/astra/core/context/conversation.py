class Conversation:

    def __init__(self):
        self.messages = []

    def add(self, speaker, text):

        self.messages.append(
            {
                "speaker": speaker,
                "text": text
            }
        )

    def latest(self):

        if self.messages:
            return self.messages[-1]

        return None

    def all(self):

        return self.messages

    def clear(self):
        self.messages = []