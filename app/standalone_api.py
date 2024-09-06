import os

import aiofiles
from aiohttp import web

from plugins.standalone.app.standalone_svc import StandaloneService
from plugins.standalone.util.exception_handler import exception_handler

class StandaloneApi:

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')
        self.data_svc = services.get('data_svc')
        self.standalone_svc = StandaloneService(services=services)

    async def get_data(self, request):
        adversaries = sorted([a.display for a in await self.data_svc.locate('adversaries')],
                             key=lambda a: a['name'])
        planners = sorted([p.display for p in await self.data_svc.locate('planners')],
                          key=lambda p: p['name'])
        return web.json_response(dict(adversaries=adversaries, planners=planners))
    @exception_handler
    async def download_standalone_agent(self, request):
        data = dict(await request.json())
        print(data)
        file_path = ''
        content_type = 'application/zip'
        if data['extension'] == '.tar.gz':
            print('Download tar.gz agent is run')
            file_path = await self.standalone_svc.create_tar(adversary_id=data["adversary_id"], planner_id=data["planner_id"])
            content_type = 'application/gzip'
        elif data['extension'] == '.zip':
            file_path = await self.standalone_svc.create_zip(adversary_id=data["adversary_id"], planner_id=data["planner_id"])
        try:
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    'Content-Disposition': f'attachment; filename={os.path.basename(file_path)}',
                    'Content-Type': f'{content_type}',
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
            adversary = await self.standalone_svc.get_adversary_by_id(adversary_id=adversary_id)
            abilities = await self.standalone_svc.get_abilities_by_adversary(adversary)
            ret = []
            for ability in abilities:
                ret.append({
                    "ability": ability['ability_id'],
                    "payloads": self.standalone_svc.get_payload_paths(ability=ability)
                })
            return web.json_response(dict(abilties=ret))
        except Exception as err:
            print(err)
            return web.json_response(dict(msg="err"))
