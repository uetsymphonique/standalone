class AgentLink:
    def __init__(self, ability=None):
        self.ability = ability

    def __repr__(self):
        return str(self.__dict__)