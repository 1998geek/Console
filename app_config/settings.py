import os
import json

_CONFIG_DIR = os.path.dirname(__file__)
_SETTINGS_FILE = os.path.join(_CONFIG_DIR, 'app_settings.json')

DEFAULT_SETTINGS = {
    "IMAGE_BATCH_THRESHOLD": 3
}

def load_settings():
    """
    Loads settings from the JSON file.
    If the file doesn't exist or is invalid, returns default settings.
    """
    if not os.path.exists(_SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(_SETTINGS_FILE, 'r', encoding='utf-8') as f:
            # Merge loaded settings with defaults to ensure all keys are present
            loaded = json.load(f)
            settings = DEFAULT_SETTINGS.copy()
            settings.update(loaded)
            return settings
    except (IOError, json.JSONDecodeError):
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """
    Saves the settings dictionary to the JSON file.
    """
    try:
        with open(_SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except IOError as e:
        raise IOError(f"Error writing settings file: {e}")

def get_setting(key):
    """
    Gets a specific setting value by key.
    """
    settings = load_settings()
    return settings.get(key)

def update_setting(key, value):
    """
    Updates a specific setting and saves it.
    """
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
