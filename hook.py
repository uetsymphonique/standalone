from plugins.standalone.app.standalone_api import StandaloneApi

name = 'Standalone'
description = 'Standalone api'
address = '/plugin/standalone/gui'


async def enable(services):
    app = services.get('app_svc').application
    standalone_api = StandaloneApi(services=services)
    # app.router.add_route('GET', '/plugin/standalone/api', standalone_api.splash)
    app.router.add_route('GET', '/plugin/standalone/show', standalone_api.get_data)
    app.router.add_route('GET', '/plugin/standalone/get_adversaries', standalone_api.get_adversaries)
    app.router.add_route('GET', '/plugin/standalone/get_planners', standalone_api.get_planners)
    app.router.add_route('GET', '/plugin/standalone/get_sources', standalone_api.get_sources)
    # app.router.add_route('GET', '/plugin/standalone/get_obfuscators', standalone_api.get_obfuscators)
    app.router.add_route('POST', '/plugin/standalone/download', standalone_api.download_standalone_agent)
    app.router.add_route('GET', '/plugin/standalone/abilities/{adversary_id}', standalone_api.get_abilities)
