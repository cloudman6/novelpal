from box import Box
import yaml
import os

class ConfigManager:
    def __init__(self, config_file='config/settings.yaml'):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file):
        config_path = os.path.join(os.path.dirname(__file__), '..', config_file)
        with open(config_path, 'r', encoding='utf-8') as file:
            return Box(yaml.safe_load(file), default_box=True, default_box_attr=None)

    def get_config(self):
        return self.config 