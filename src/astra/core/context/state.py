class State:

    def __init__(self):

        self.values = {}

    def set(self, key, value):

        self.values[key] = value

    def get(self, key):

        return self.values.get(key)

    def all(self):

        return self.values

    def clear(self):
        self.values = {}