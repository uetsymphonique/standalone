import aiofiles
import os
from aiohttp import web
from aiohttp_jinja2 import template
from plugins.standalones.app.standalone_svc import StandaloneService


class StandaloneApi:

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')
        self.data_svc = services.get('data_svc')
        self.stanalone_svc = StandaloneService(services=services)

    async def get_data(self, request):
        adversaries = sorted([a.display for a in await self.data_svc.locate('adversaries')],
                             key=lambda a: a['name'])
        planners = sorted([p.display for p in await self.data_svc.locate('planners')],
                          key=lambda p: p['name'])
        return web.json_response(dict(adversaries=adversaries, planners=planners))

    async def download_standalone_agent(self, request):
        data = dict(await request.json())
        abilities = await self.stanalone_svc.get_abilities_by_adversary(data['adversary_id'])
        file_path = await self.stanalone_svc.create_zip(abilities=abilities)
        try:
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Disposition': f'attachment; filename={os.path.basename(file_path)}',
                    'Content-Type': 'application/zip',
                }
            )

            await response.prepare(request)

            async with aiofiles.open(file_path, mode='rb') as f:
                chunk = await f.read(1024)  # Read the file in chunks
                while chunk:
                    await response.write(chunk)
                    chunk = await f.read(1024)

            await response.write_eof()
            os.remove(file_path)  # Delete the ZIP file after the response is sent
            return response
        except Exception as e:
            print(e)
            return web.json_response(dict(msg="error!"))

    async def get_abilities(self, request):
        adversary_id = request.match_info.get("adversary_id")
        print(f'Adversary ID: {adversary_id}')
        try:
            abilities = await self.stanalone_svc.get_abilities_by_adversary(adversary_id)
            ret = []
            for ability in abilities:
                ret.append({
                    "ability": ability['ability_id'],
                    "payloads": self.stanalone_svc.get_payload_paths(ability=ability)
                })
            return web.json_response(dict(abilties=ret))
        except Exception as err:
            print(err)
            return web.json_response(dict(msg="err"))
