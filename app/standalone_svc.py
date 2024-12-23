import fnmatch
import glob
import logging
import os
import shutil
import tarfile
import zipfile

import yaml

from app.utility.base_service import BaseService
from plugins.standalone.util.exception_handler import async_exception_handler

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
PLUGIN_ROOT = os.path.join(APP_ROOT, '../..')
CALDERA_ROOT = os.path.join(PLUGIN_ROOT, '..')

TMP_DIR = os.path.join(APP_ROOT, '../tmp')
CALDER_ALONE = os.path.join(APP_ROOT, '../calder-alone')
PAYLOADS_FOLDER = TMP_DIR
REMOVING_GLOBS = ['.git*', 'img*', '*.md', '*.py', 'app/*', 'plugins/*/app/*', 'plugins/*/*.py', 'requirements.txt']
EXCEPTION_GLOBS = [
    'app/data_encoders',
    'app/learning',
    'app/contacts',
    'plugins/*/app/data_encoders',
    'plugins/*/app/packers'
]

DATA_FOLDER = os.path.join(TMP_DIR, 'data')
SOURCES_FOLDER = os.path.join(DATA_FOLDER, 'sources')
ABILITIES_FOLDER = os.path.join(DATA_FOLDER, 'abilities')

ADVERSARY = os.path.join(DATA_FOLDER, 'adversary.yml')
PLANNER = os.path.join(DATA_FOLDER, 'planner.yml')
SOURCE = os.path.join(DATA_FOLDER, 'source.yml')
EXEC_INFO = os.path.join(DATA_FOLDER, 'exec.txt')


class BreakLoop(Exception): pass


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
                logging.debug(f'Adversary "{a.display["name"]}" found')
                return a.display
        logging.error(f'Could not find adversary: {adversary_id}')
        return None

    @async_exception_handler
    async def get_source_by_id(self, source_id):
        for s in await self.data_svc.locate('sources'):
            if s.display['id'] == source_id:
                logging.debug(f'Source "{s.display["name"]}" found')
                return s.display
        logging.error(f'Could not find source: {source_id}')
        return None

    @async_exception_handler
    async def get_planner_by_id(self, planner_id):
        for p in await self.data_svc.locate('planners'):
            if p.display['id'] == planner_id:
                logging.debug(f'Planner "{p.display["name"]}" found')
                return p
        logging.error(f'Could not find planner: {planner_id}')
        return None

    @async_exception_handler
    async def get_abilities_by_adversary(self, adversary):
        abilities = [a.display for a in await self.data_svc.locate('abilities') if
                     a.display['ability_id'] in adversary["atomic_ordering"]]
        return abilities

    @async_exception_handler
    async def get_payload_paths(self, ability):
        executors = ability['executors']
        payloads = set()
        for executor in executors:
            payloads.update([p for p in executor['payloads']])
        payload_paths = []
        for payload in payloads:
            payload_dirs = [os.path.join(CALDERA_ROOT, f"plugins/{plugin.name}/payloads") for plugin in
                            await self.data_svc.locate('plugins')] + [os.path.join(CALDERA_ROOT, f"data/payloads")]
            try:
                for payload_dir in payload_dirs:
                    for folder_name, subfolders, file_names in os.walk(payload_dir):
                        for file_name in file_names:
                            if file_name == payload:
                                path = os.path.join(folder_name, file_name)
                                payload_paths.append(path)
                                raise BreakLoop
                logging.warning(f"Can't find payload \"{payload}\"")
            except BreakLoop:
                pass
        return payload_paths

    @staticmethod
    async def get_ability_path(ability):
        path = os.path.join(PLUGIN_ROOT,
                            f'{ability["plugin"]}/data/abilities/{ability["tactic"]}/{ability["ability_id"]}.yml')
        if not os.path.isfile(path):
            path = os.path.join(CALDERA_ROOT, f'data/abilities/{ability["tactic"]}/{ability["ability_id"]}.yml')
        return path

    @staticmethod
    async def get_planner_path(planner):
        return os.path.join(CALDERA_ROOT, '/'.join(
            planner.module.replace("app", "data").replace(planner.name, planner.planner_id).split('.')) + ".yml")

    @staticmethod
    @async_exception_handler
    async def _make_tmp_dir():
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        shutil.copytree(CALDER_ALONE, TMP_DIR)
        os.makedirs(PAYLOADS_FOLDER, exist_ok=True)
        if os.path.exists(ABILITIES_FOLDER):
            shutil.rmtree(ABILITIES_FOLDER)
        for pattern in REMOVING_GLOBS:
            full_pattern = os.path.join(TMP_DIR, pattern)
            for file_path in glob.glob(full_pattern):
                try:
                    if any(fnmatch.fnmatch(file_path, os.path.join(TMP_DIR, exception)) for exception in
                           EXCEPTION_GLOBS):
                        logging.info(f"Skipping {file_path} (matches exception pattern)")
                        continue
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        logging.info(f"File {file_path} was deleted!")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        logging.info(f"Folder {file_path} was deleted!")
                except Exception as e:
                    logging.info(f"Error in deleting {file_path}: {e}")
        os.remove(ADVERSARY)
        os.remove(SOURCE)
        os.remove(PLANNER)
        os.makedirs(ABILITIES_FOLDER, exist_ok=True)

    @async_exception_handler
    async def _generate_adversary_and_ability_files(self, adversary_id):
        """
        Generates an adversary file based on the provided adversary ID.
        """
        adversary = await self.get_adversary_by_id(adversary_id=adversary_id)
        logging.info(f'Generate adversary.yml for: \"{adversary["name"]}\"')
        with open(ADVERSARY, 'w') as adversary_file:
            yaml.dump(adversary, adversary_file)
        abilities = await self.get_abilities_by_adversary(adversary=adversary)
        payload_paths = set()
        logging.info(f'Dumping abilities of the chosen adversary "{adversary["name"]}"')
        for ability in abilities:
            # ability_path = await self.get_ability_path(ability)
            payload_paths.update(await self.get_payload_paths(ability))
            tactic_folder = os.path.join(ABILITIES_FOLDER, ability["tactic"])
            os.makedirs(tactic_folder, exist_ok=True)
            # if os.path.isfile(ability_path):
            #     shutil.copy(ability_path, tactic_folder)
            #     # logging.info(f'{ability["ability_id"]} was copied')
            # else:
            #     logging.warning(f"Ability file not found {ability_path}")
            yaml_file_path = os.path.join(tactic_folder, f'{ability["ability_id"]}.yml')
            if 'ability_id' in ability:
                ability["id"] = ability.pop('ability_id', None)
            abs = [ability]
            with open(yaml_file_path, 'w') as yaml_file:
                yaml.dump(abs, yaml_file)
                logging.info(f'YAML file for ability "{ability["name"]}" was dumped')
        logging.info(f'Copying payloads for "{adversary["name"]}"')
        for payload_path in payload_paths:
            if os.path.isfile(payload_path):
                shutil.copy(payload_path, PAYLOADS_FOLDER)
                logging.info(f'Payload "{os.path.basename(payload_path)}" was copied from {payload_path}')
            else:
                logging.warning(f"Payload not found {payload_path}")

    @async_exception_handler
    async def _generate_planner_file(self, planner_id):
        """
        Generates a planner file based on the provided planner ID.
        """
        planner = await self.get_planner_by_id(planner_id=planner_id)
        planner_path = await self.get_planner_path(planner)
        logging.info(f'Copy planner "{planner.name}" for agent')
        if os.path.isfile(planner_path):
            shutil.copy(planner_path, PLANNER)
        else:
            logging.warning(f"Planner not found {planner_path}")

    @async_exception_handler
    async def _generate_source_file(self, source_id):
        """
        Generates a source file based on the provided source ID.
        """
        source = await self.get_source_by_id(source_id=source_id)
        logging.info(f'Generate source "{source["name"]}" for agent')
        with open(SOURCE, 'w') as source_file:
            yaml.dump(source, source_file)

    @async_exception_handler
    async def _copy_calder_alone(self, platform):
        if platform not in ["windows", "linux"]:
            logging.error(f"Platform is invalid {platform}")
            return
        print(f'[+] Copying calder-alone-{platform}...')
        agent_path = os.path.join(CALDER_ALONE, f'calder-alone-{platform}')
        shutil.copy(agent_path, TMP_DIR)

    @staticmethod
    async def _inform_platform_and_executors(platform, executors):
        logging.info(f'Informing platform: {platform}')
        logging.info(f'Informing executors: {", ".join(executors)}')
        with open(EXEC_INFO, 'w') as f:
            f.write(platform)
            f.write("\n")
            f.write(", ".join(executors))

    @async_exception_handler
    async def _encapsulating_resources(self, adversary_id, planner_id, source_id=None,
                                       platform=None, executors=None):
        await self._make_tmp_dir()
        await self._generate_adversary_and_ability_files(adversary_id)
        await self._generate_source_file(source_id)
        await self._generate_planner_file(planner_id)
        await self._inform_platform_and_executors(platform, executors)

    @staticmethod
    @async_exception_handler
    async def remove_resources():
        logging.info(f'Cleanup {TMP_DIR}')
        shutil.rmtree(TMP_DIR)

    @async_exception_handler
    async def create_zip(self, adversary_id, planner_id, source_id, platform, executors):
        await self._encapsulating_resources(adversary_id=adversary_id, planner_id=planner_id, source_id=source_id,
                                            platform=platform, executors=executors)
        zip_file_path = os.path.join(TMP_DIR, '../standalone.zip')
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for folder_name, subfolders, file_names in os.walk(TMP_DIR):
                for file_name in file_names:
                    file_path = os.path.join(folder_name, file_name)
                    zip_file.write(file_path, os.path.relpath(file_path, TMP_DIR))
        return zip_file_path

    @async_exception_handler
    async def create_tar(self, adversary_id, planner_id, source_id, platform, executors):
        await self._encapsulating_resources(adversary_id=adversary_id, planner_id=planner_id, source_id=source_id,
                                            platform=platform, executors=executors)
        tar_file_path = os.path.join(TMP_DIR, '../standalone.tar.gz')
        with tarfile.open(tar_file_path, 'w:gz') as tar_file:
            tar_file.add(TMP_DIR, arcname='standalone')
        return tar_file_path
