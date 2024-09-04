import marshmallow as ma

class AbilitySchema(ma.Schema):
    ability_id = ma.fields.String()
    tactic = ma.fields.String(load_default=None)
    technique_name = ma.fields.String(load_default=None)
    technique_id = ma.fields.String(load_default=None)
    name = ma.fields.String(load_default=None)
    description = ma.fields.String(load_default=None)