class History:

    def __init__(self):

        self.commands = []

    def add(self, command):

        self.commands.append(command)

    def last(self):

        if self.commands:
            return self.commands[-1]

        return None

    def all(self):

        return self.commands

    def clear(self):
        self.commands = []