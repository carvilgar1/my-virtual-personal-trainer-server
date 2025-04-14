import glob
import importlib.util
import logging
import os

from src.constants import DEFAULT_LANGUAGE

_application_locales = {}

def load_locales():
    """
    Load all localization files from the src/locales directory.
    """
    locales_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'locales')
    locale_files = glob.glob(os.path.join(locales_dir, '*.py'))

    for file_path in locale_files:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'locales'):
            _application_locales[module_name] = module.locales

print(os.scandir('./src'))


def localize(key: str, language: str = DEFAULT_LANGUAGE) -> str:
    """
    Localize a key using the provided language.
    """
    if language not in _application_locales:
        logging.warning(
            f"Language '{language}' not found. Falling back to '{DEFAULT_LANGUAGE}'.")
        language = DEFAULT_LANGUAGE

    if key not in _application_locales[language]:
        logging.warning(f"Key '{key}' not found in language '{language}'.")
        return key

    return _application_locales[language][key]
