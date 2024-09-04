import marshmallow as ma

class RequirementSchema(ma.Schema):
    module = ma.fields.String()
    relationship_match = ma.fields.List(ma.fields.Dict())

    @ma.post_load()
    def build_requirement(self, data, **_):
        return Requirement(**data)

class Requirement:

    schema = RequirementSchema()

    def unique(self):
        return self.module

    def __init__(self, module, relationship_match):
        super().__init__()
        self.module = module
        self.relationship_match = relationship_match
