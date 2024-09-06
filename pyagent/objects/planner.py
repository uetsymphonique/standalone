import uuid


class AgentPlanner:
    def __init__(self, data=None, name='', planner_id='', module='', params=None, stopping_conditions=None, description=None,
                 ignore_enforcement_modules=(), allow_repeatable_abilities=False, plugin=''):
        if data:
            for key, value in data.items():
                setattr(self, key, value)
            return
        self.name = name
        self.planner_id = planner_id if planner_id else str(uuid.uuid4())
        self.module = module
        self.params = params if params else {}
        self.description = description
        self.stopping_conditions = stopping_conditions
        self.ignore_enforcement_modules = ignore_enforcement_modules
        self.allow_repeatable_abilities = allow_repeatable_abilities
        self.plugin = plugin
