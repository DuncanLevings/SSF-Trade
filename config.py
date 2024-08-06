import yaml
from enum import Enum
from pathlib import Path

def get_settings_file_path():
    return Path.cwd() / "settings.yaml"

settings_file_path = get_settings_file_path()

if not settings_file_path.is_file():
    raise FileNotFoundError(f"Settings file '{settings_file_path}' not found.")

with open(settings_file_path, "r") as file:
    config = yaml.safe_load(file)

database_name = config['league']['name']

def get_league_name():
    return config['league']['name']

def create_enum(name, values):
    return Enum(name, values)

Rarity = create_enum('Rarity', config['rarity'])
SubClass = create_enum('SubClass', config['sub_class'])
UniqueClass = create_enum('UniqueClass', config['unique_class'])
CleanClusterName = create_enum('CleanClusterName', config['clean_cluster_name'])
CleanFlaskName = create_enum('CleanFlaskName', config['clean_flask_name'])
ItemName = create_enum('ItemName', config['item_name'])
Influence = create_enum('Influence', config['influence'])
BossMap = create_enum('BossMap', config['boss_map'])
CheckUnique = create_enum('CheckUnique', config['check_unique'])