import uuid

from collections.abc import Iterable


class AgentAbility:
    def __init__(self, data=None, ability_id='', name=None, description=None, tactic=None, technique_id=None,
                 technique_name=None,
                 executors=(), requirements=None, privilege=None, repeatable=False, buckets=None, access=None,
                 additional_info=None, tags=None, singleton=False, plugin='', delete_payload=True, **kwargs):
        if data:
            for key, value in data.items():
                setattr(self, key, value)
            return
        self.ability_id = ability_id if ability_id else str(uuid.uuid4())
        self.tactic = tactic.lower() if tactic else None
        self.technique_name = technique_name
        self.technique_id = technique_id
        self.name = name
        self.description = description
        self.executors = executors
        self.requirements = requirements if requirements else []
        self.privilege = privilege
        self.repeatable = repeatable
        self.buckets = buckets if buckets else []
        self.singleton = singleton
        self.access = access
        self.additional_info = additional_info or dict()
        self.additional_info.update(**kwargs)
        self.tags = set(tags) if tags else set()
        self.plugin = plugin
        self.delete_payload = delete_payload

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        ret = ''
        for key, val in self.__dict__.items():
            ret += f'{key}:\n{print_val(val)}\n'
        return ret



def print_val(inp):
    return '\n'.join([f'    {element}' for element in inp]) if not isinstance(inp, str) and isinstance(inp,
                                                                                                       Iterable) else f'    {str(inp)}'
