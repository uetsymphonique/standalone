import os
import zipfile
import yaml
import shutil
import tempfile

from app.utility.base_service import BaseService
from app.api.v2.handlers.adversary_api import AdversaryApi

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
TMP_DIR = os.path.join(APP_ROOT, '../tmp')
PLUGIN_ROOT = os.path.join(APP_ROOT, '../..')

class StandaloneService(BaseService):
    def __init__(self, services):
        self.services = services
        self.app_svc = services.get('app_svc')
        self.file_svc = services.get('file_svc')
        self.data_svc = services.get('data_svc')
    
    async def get_ability_ids_by_adversary(self, adversary_id):
        for a in await self.data_svc.locate('adversaries'):
            if a.display['adversary_id'] == adversary_id:
                return a.display['atomic_ordering']
        return None
    
    async def get_abilities_by_adversary(self, adversary_id):
        ids = await self.get_ability_ids_by_adversary(adversary_id=adversary_id)
        abilities = [a.display for a in await self.data_svc.locate('abilities') if a.display['ability_id'] in ids]
        return abilities

    def get_payload_paths(self, ability):
        executors = ability['executors']
        payloads = set()
        for executor in executors:
            payloads.update([p for p in executor['payloads']])
        return [os.path.join(PLUGIN_ROOT, str(ability['plugin']) + f"/payloads/{payload}") for payload in payloads]
    

    async def create_zip(self, abilities):
        zip_file_path = os.path.join(TMP_DIR, 'files.zip')
        os.makedirs(TMP_DIR, exist_ok=True)
        with zipfile.ZipFile(zip_file_path, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
            payload_paths = set()
            for ability in abilities:
                file_path = os.path.join(TMP_DIR, f'{ability["ability_id"]}.yml')
                with open(file_path, 'w') as f:
                    yaml.dump(ability, f)
                    # print(f'{file_path} created')
                zip_file.write(file_path, os.path.basename(file_path))
                os.remove(file_path)
                payload_paths.update(self.get_payload_paths(ability))
            
            for payload_path in payload_paths:
                # zip_file.write(payload_paths, os.path.basename(payload_path))
                print(f'{payload_path} exists: {os.path.exists(payload_path)}')
            # print(payload_paths)
        # print(zip_file_path)
        return zip_file_path
