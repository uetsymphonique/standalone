import uuid


class AgentAdversary:
    def __init__(self, data=None, name='', adversary_id='', description='', atomic_ordering=(), objective='', tags=None, plugin=''):
        if data:
            for key, value in data.items():
                setattr(self, key, value)
            return
        self.adversary_id = adversary_id if adversary_id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.atomic_ordering = atomic_ordering
        self.objective = objective
        self.tags = set(tags) if tags else set()
        self.has_repeatable_abilities = False
        self.plugin = plugin
