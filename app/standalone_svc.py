import os
import shutil
import tarfile
import zipfile

import yaml
from app.utility.base_service import BaseService
from plugins.standalone.util.exception_handler import async_exception_handler, exception_handler

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
PLUGIN_ROOT = os.path.join(APP_ROOT, '../..')

TMP_DIR = os.path.join(APP_ROOT, '../tmp')
PYAGENT_DIR = os.path.join(APP_ROOT, '../pyagent')
PAYLOADS_FOLDER = os.path.join(TMP_DIR, 'payloads')

DATA_FOLDER = os.path.join(TMP_DIR, 'data')
SOURCES_FOLDER = os.path.join(DATA_FOLDER, 'sources')
ABILITIES_FOLDER = os.path.join(DATA_FOLDER, 'abilities')

ADVERSARY = os.path.join(DATA_FOLDER, 'adversary.yml')
PLANNER = os.path.join(DATA_FOLDER, 'planner.yml')


class StandaloneService(BaseService):
    def __init__(self, services):
        self.services = services
        self.app_svc = services.get('app_svc')
        self.file_svc = services.get('file_svc')
        self.data_svc = services.get('data_svc')

    @async_exception_handler
    async def get_adversary_by_id(self, adversary_id):
        for a in await self.data_svc.locate('adversaries'):
            if a.display['adversary_id'] == adversary_id:
                return a.display
        return None

    @async_exception_handler
    async def get_planner_by_id(self, planner_id):
        for p in await self.data_svc.locate('planners'):
            if p.display['id'] == planner_id:
                # print(p.display)
                return p.display
        return None

    @async_exception_handler
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
    @exception_handler
    def _make_tmp_dir():
        # os.makedirs(TMP_DIR, exist_ok=True)
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        shutil.copytree(PYAGENT_DIR, TMP_DIR)
        os.makedirs(PAYLOADS_FOLDER, exist_ok=True)
        os.makedirs(DATA_FOLDER, exist_ok=True)
        os.makedirs(ABILITIES_FOLDER, exist_ok=True)
        os.makedirs(SOURCES_FOLDER, exist_ok=True)

    @async_exception_handler
    async def _encapsulating_resources(self, adversary_id, planner_id=None):
        self._make_tmp_dir()

        '''
        Dump adversary into yaml file
        '''
        adversary = await self.get_adversary_by_id(adversary_id=adversary_id)
        print('[+] Generate adversary for agent ...\n')
        with open(ADVERSARY, 'w') as adversary_file:
            yaml.dump(adversary, adversary_file)

        '''
        Dump planner into yaml file
        '''
        planner = await self.get_planner_by_id(planner_id=planner_id)
        print('[+] Generate planner for agent ...\n')
        with open(PLANNER, 'w') as planner_file:
            yaml.dump(planner, planner_file)

        '''
        Dump abilities into yaml files and get payloads
        '''
        abilities = await self.get_abilities_by_adversary(adversary=adversary)
        payload_paths = set()
        print('[+] Generate abilities of the chosen adversary ...\n')
        for ability in abilities:
            ability_path = self.get_ability_path(ability)
            # print(ability_path)
            tactic_folder = os.path.join(ABILITIES_FOLDER, ability["tactic"])
            os.makedirs(tactic_folder, exist_ok=True)
            yaml_file_path = os.path.join(tactic_folder, f'{ability["ability_id"]}.yml')
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(ability, yaml_file)
            payload_paths.update(self.get_payload_paths(ability))
        print('[+] Copy payloads ...\n')
        for payload_path in payload_paths:
            if os.path.isfile(payload_path):
                shutil.copy(payload_path, PAYLOADS_FOLDER)
            else:
                print(f"File not found {payload_path}")

    @staticmethod
    @exception_handler
    def remove_resources():
        print(f'[+] Cleanup {TMP_DIR}')
        shutil.rmtree(TMP_DIR)

    async def create_zip(self, adversary_id, planner_id):
        await self._encapsulating_resources(adversary_id=adversary_id, planner_id=planner_id)
        zip_file_path = os.path.join(TMP_DIR, '../standalone.zip')
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for folder_name, subfolders, file_names in os.walk(TMP_DIR):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    zip_file.write(file_path, os.path.relpath(file_path, TMP_DIR))
        return zip_file_path

    @async_exception_handler
    async def create_tar(self, adversary_id, planner_id):
        await self._encapsulating_resources(adversary_id=adversary_id, planner_id=planner_id)
        tar_file_path = os.path.join(TMP_DIR, '../standalone.tar.gz')
        with tarfile.open(tar_file_path, 'w:gz') as tar_file:
            tar_file.add(TMP_DIR, arcname='standalone')
        # self.remove_resources()
        return tar_file_path
