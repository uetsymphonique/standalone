from plugins.standalone.app.standalone_api import StandaloneApi
from app.service.auth_svc import check_authorization


name = 'Standalone'
description = 'Standalone api'
address = '/plugin/standalone/gui'


async def enable(services):
    app = services.get('app_svc').application
    standalone_api = StandaloneApi(services=services)
    app.router.add_route('GET', '/plugin/standalone/show', standalone_api.get_data)
    app.router.add_route('POST', '/plugin/standalone/download', standalone_api.download_standalone_agent)
    app.router.add_route('GET', '/plugin/standalone/abilities/{adversary_id}', standalone_api.get_abilities)


