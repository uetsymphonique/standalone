import logging
import os

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader
from aiohttp import web

from plugins.standalone.app.standalone_svc import StandaloneService
from plugins.standalone.util.exception_handler import async_exception_handler


class StandaloneApi:

    def __init__(self, services):
        self.auth_svc = services.get('auth_svc')
        self.data_svc = services.get('data_svc')
        self.log = logging.getLogger('standalone_api')
        self.standalone_svc = StandaloneService(services=services)

    @async_exception_handler
    async def get_data(self, request):
        adversaries = sorted([a.display for a in await self.data_svc.locate('adversaries')],
                             key=lambda a: a['name'])
        planners = sorted([p.display for p in await self.data_svc.locate('planners')],
                          key=lambda p: p['name'])
        sources = sorted([s.display for s in await self.data_svc.locate('sources')],
                         key=lambda s: s['name'])
        obfuscators = sorted([o.display for o in await self.data_svc.locate('obfuscators')],
                             key=lambda o: o['name'])
        return web.json_response(
            dict(adversaries=adversaries, planners=planners, sources=sources, obfuscators=obfuscators))

    @async_exception_handler
    async def get_adversaries(self, request):
        adversaries = sorted([a.display for a in await self.data_svc.locate('adversaries')],
                             key=lambda a: a['name'])
        return web.json_response(dict(adversaries=[dict(
            adversary_id=a["adversary_id"], name=a["name"]) for a in adversaries
        ]))

    @async_exception_handler
    async def get_abilities(self, request):
        abilities = sorted([a.display for a in await self.data_svc.locate('abilities')],
                           key=lambda a: a['name'])
        return web.json_response(dict(abilities=[dict(
            ability_id=a["ability_id"], name=a["name"]) for a in abilities
        ]))

    @async_exception_handler
    async def get_planners(self, request):
        planners = sorted([p.display for p in await self.data_svc.locate('planners')],
                          key=lambda p: p['name'])
        return web.json_response(dict(planners=[dict(
            planner_id=p["id"], name=p["name"]) for p in planners
        ]))

    @async_exception_handler
    async def get_sources(self, request):
        sources = sorted([s.display for s in await self.data_svc.locate('sources')],
                         key=lambda s: s['name'])
        return web.json_response(dict(sources=[dict(
            source_id=s["id"], name=s["name"]) for s in sources
        ]))

    @async_exception_handler
    async def download_standalone_agent(self, request):
        data = dict(await request.json())
        # print(data)
        file_path = ''
        content_type = 'application/zip'
        if data['extension'] == '.tar.gz':
            file_path = await self.standalone_svc.create_tar(adversary_id=data["adversary_id"],
                                                             planner_id=data["planner_id"],
                                                             source_id=data["source_id"],
                                                             platform=data["platform"],
                                                             executors=data["executors"])
            content_type = 'application/gzip'
        elif data['extension'] == '.zip':
            file_path = await self.standalone_svc.create_zip(adversary_id=data["adversary_id"],
                                                             planner_id=data["planner_id"],
                                                             source_id=data["source_id"],
                                                             platform=data["platform"],
                                                             executors=data["executors"])
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

            f: AsyncBufferedReader
            async with aiofiles.open(file_path, mode='rb') as f:
                chunk = await f.read(1024)  # Read the file in chunks
                while chunk:
                    await response.write(chunk)
                    chunk = await f.read(1024)

            await response.write_eof()
            os.remove(file_path)
            logging.info(f'Cleanup {file_path}')
            await self.standalone_svc.remove_resources()
            return response
        except Exception as e:
            print(e)
            return web.json_response(dict(msg="error!"))

    @async_exception_handler
    async def get_abilities(self, request):
        adversary_id = request.match_info.get("adversary_id")
        # print(f'Adversary ID: {adversary_id}')
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
