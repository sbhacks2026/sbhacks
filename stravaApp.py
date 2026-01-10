import json

def get_keys(path='config.json'):
    try:
        with open(path, 'r') as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file {path} not found.")
        return None

config = get_keys()
api_key = config.get('api_key')
print(f"Key loaded: {api_key}")