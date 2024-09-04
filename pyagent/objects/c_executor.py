import marshmallow as ma


class ExecutorSchema(ma.Schema):
    name = ma.fields.String(load_default=None)
    platform = ma.fields.String(load_default=None)
    command = ma.fields.String(load_default=None)
    code = ma.fields.String(load_default=None)
    language = ma.fields.String(load_default=None)
    build_target = ma.fields.String(load_default=None)
    payloads = ma.fields.List(ma.fields.String())
    uploads = ma.fields.List(ma.fields.String())
    timeout = ma.fields.Int(load_default=60)
