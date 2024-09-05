import uuid


class Ability:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
            return str(self.__dict__)