import json
import os

def load_priorities():
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    priorities = [(item['id'], item['name']) for item in config.get('priorities', [])]
    return priorities