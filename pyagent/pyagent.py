import os

import yaml

from objects.c_ability import Ability

AGENT_ROOT = os.path.abspath(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(AGENT_ROOT, 'data')
for folder_name, subfolders, file_names in os.walk(DATA_FOLDER):
    for file_name in file_names:
        file_path = os.path.join(folder_name, file_name)
        with open(file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
            ability = Ability(data)
            print(ability)
            print('-------------------')
