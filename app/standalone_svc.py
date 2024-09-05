import os
import shutil
import tarfile
import zipfile

import yaml
from app.utility.base_service import BaseService

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
PLUGIN_ROOT = os.path.join(APP_ROOT, '../..')

TMP_DIR = os.path.join(APP_ROOT, '../tmp')
PAYLOADS_FOLDER = os.path.join(TMP_DIR, 'payloads')

DATA_FOLDER = os.path.join(TMP_DIR, 'data')
SOURCES_FOLDER = os.path.join(DATA_FOLDER, 'sources')
ABILITIES_FOLDER = os.path.join(DATA_FOLDER, 'abilities')

ATOMIC_ORDERING = os.path.join(TMP_DIR, 'atomic_ordering.txt')



class StandaloneService(BaseService):
    def __init__(self, services):
        self.services = services
        self.app_svc = services.get('app_svc')
        self.file_svc = services.get('file_svc')
        self.data_svc = services.get('data_svc')

    async def get_adversary_by_id(self, adversary_id):
        for a in await self.data_svc.locate('adversaries'):
            if a.display['adversary_id'] == adversary_id:
                return a.display
        return None

    async def get_abilities_by_adversary(self, adversary):
        abilities = [a.display for a in await self.data_svc.locate('abilities') if
                     a.display['ability_id'] in adversary["atomic_ordering"]]
        return abilities

    @staticmethod
    def get_payload_paths(ability):
        executors = ability['executors']
        payloads = set()
        for executor in executors:
            payloads.update([p for p in executor['payloads']])
        return [os.path.join(PLUGIN_ROOT, str(ability['plugin']) + f"/payloads/{payload}") for payload in payloads]

    @staticmethod
    def get_ability_path(ability):
        return os.path.join(PLUGIN_ROOT,
                            f'{ability["plugin"]}/data/abilities/{ability["tactic"]}/{ability["ability_id"]}.yml')

    @staticmethod
    def _make_tmp_dir():
        os.makedirs(TMP_DIR, exist_ok=True)
        os.makedirs(PAYLOADS_FOLDER, exist_ok=True)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        os.makedirs(ABILITIES_FOLDER, exist_ok=True)
        os.makedirs(SOURCES_FOLDER, exist_ok=True)

    async def _encapsulating_resources(self, adversary_id):
        adversary = await self.get_adversary_by_id(adversary_id=adversary_id)
        abilities = await self.get_abilities_by_adversary(adversary=adversary)
        self._make_tmp_dir()
        payload_paths = set()
        with open(ATOMIC_ORDERING, 'w') as atomic_ordering:
            for ability in abilities:
                atomic_ordering.write(ability["ability_id"] + '\n')
        # print('copy abilities')
        for ability in abilities:
            ability_path = self.get_ability_path(ability)
            # print(ability_path)
            tactic_folder = os.path.join(ABILITIES_FOLDER, ability["tactic"])
            os.makedirs(tactic_folder, exist_ok=True)
            yaml_file_path = os.path.join(tactic_folder, f'{ability["ability_id"]}.yml')
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(ability, yaml_file)
            # if os.path.isfile(ability_path):
            #     tactic_folder = os.path.join(ABILITIES_FOLDER, ability["tactic"])
            #     os.makedirs(tactic_folder, exist_ok=True)
            #     shutil.copy(ability_path, tactic_folder)
            # else:
            #     print(f"File not found {ability_path}")
            payload_paths.update(self.get_payload_paths(ability))
        # print('copy payloads')
        for payload_path in payload_paths:
            if os.path.isfile(payload_path):
                shutil.copy(payload_path, PAYLOADS_FOLDER)
            else:
                print(f"File not found {payload_path}")

    @staticmethod
    def _remove_resources():
        os.remove(ATOMIC_ORDERING)
        shutil.rmtree(DATA_FOLDER)
        shutil.rmtree(PAYLOADS_FOLDER)

    async def create_zip(self, adversary_id):
        await self._encapsulating_resources(adversary_id=adversary_id)
        zip_file_path = os.path.join(TMP_DIR, 'standalone.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(ATOMIC_ORDERING, os.path.basename(ATOMIC_ORDERING))

            for folder_name, subfolders, file_names in os.walk(PAYLOADS_FOLDER):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    zip_file.write(file_path, os.path.relpath(file_path, TMP_DIR))

            for folder_name, subfolders, file_names in os.walk(DATA_FOLDER):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    zip_file.write(file_path, os.path.relpath(file_path, TMP_DIR))
        self._remove_resources()
        return zip_file_path

    async def create_tar(self, adversary_id):
        await self._encapsulating_resources(adversary_id=adversary_id)
        tar_file_path = os.path.join(TMP_DIR, 'standalone.tar.gz')
        with tarfile.open(tar_file_path, 'w:gz') as tar_file:
            tar_file.add(TMP_DIR, arcname='standalone')
        self._remove_resources()
        return tar_file_path
