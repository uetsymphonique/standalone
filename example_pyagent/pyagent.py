import os
import subprocess

import yaml

from objects.ability import AgentAbility
from objects.adversary import AgentAdversary
from objects.planner import AgentPlanner
from objects.secondclass.link import AgentLink

AGENT_ROOT = os.path.abspath(os.path.dirname(__file__))
DATA_FOLDER = os.path.join(AGENT_ROOT, 'data')
ABILITIES_FOLDER = os.path.join(DATA_FOLDER, 'abilities')
ADVERSARY_PATH = os.path.join(DATA_FOLDER, 'adversary.yml')
PLANNER_PATH = os.path.join(DATA_FOLDER, 'planner.yml')


class PyAgent:
    def __init__(self):
        self.links = load_links()
        self.adversary = load_adversary()
        self.planner = load_planner()
        self.output = None

    def __repr__(self):
        return str(self.__dict__)

    def run(self):
        for ability_id in self.adversary.atomic_ordering:
            for executor in self.links[ability_id].ability.executors:
                if executor['platform'] == 'linux':
                    run_command(executor['command'])


def load_links() -> dict[str, AgentLink]:
    links = dict()
    for folder_name, subfolders, file_names in os.walk(ABILITIES_FOLDER):
        for file_name in file_names:
            file_path = os.path.join(folder_name, file_name)
            with open(file_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                ability = AgentAbility(data)
                link = AgentLink(ability=ability)
                links[ability.ability_id] = link
    return links


def load_adversary() -> AgentAdversary:
    with open(ADVERSARY_PATH, 'r') as yaml_file:
        return AgentAdversary(yaml.safe_load(yaml_file))


def load_planner() -> AgentPlanner:
    with open(PLANNER_PATH, 'r') as yaml_file:
        return AgentPlanner(yaml.safe_load(yaml_file))


def run_command(command):
    try:
        # Run the command and capture the output
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        # Print the output
        print("Output:\n", result.stdout)
        print("Errors:\n", result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")


if __name__ == '__main__':
    agent = PyAgent()
    agent.run()
