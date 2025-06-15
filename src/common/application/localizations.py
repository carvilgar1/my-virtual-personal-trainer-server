import json
import logging
import os
import re

from src.constants import DEFAULT_LANGUAGE

configuration = {
    'file_pattern': r'.?locales.json',
    'fallback_language': DEFAULT_LANGUAGE
}

locales = {}


class LostFallbackLangException(Exception):
    def __init__(self, locale_key: str, fallback_language: str, file_path: str):
        super().__init__(
            f"No fallback language is configured for the locale '{locale_key}', language '{fallback_language}' is required. Check the file {file_path}")


class PlaceHolderReplacer:
    def __init__(self, placeholder_regex: str, replaces: dict[str, str]):
        self.replaces = replaces if replaces else {}
        self.placeholder_pattern = re.compile(placeholder_regex)

    def replace(self, file):
        def match_replacer(match):
            placeholder_key = match.group(1)
            return self.replaces.get(placeholder_key, match.group(0))

        return self.placeholder_pattern.sub(match_replacer, file)


def load_locales(
    root_dir: str,
    placeholder_replacer: PlaceHolderReplacer = None
) -> None:
    for root, _, files in os.walk(root_dir):
        for file in files:
            if re.match(configuration.get('file_pattern'), file):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    locales_document = f.read()
                    if placeholder_replacer:
                        locales_document = placeholder_replacer.replace(
                            locales_document)
                    json_locales = json.loads(locales_document)
                    check_fallback_lang_exists(json_locales, file_path)
                    locales.update(json_locales)


def check_fallback_lang_exists(json_locales, file_path):
    for locale_key, translations in json_locales.items():
        fallback_language = configuration.get('fallback_language')
        if not any([lang for lang in translations.keys() if lang == fallback_language]):
            raise LostFallbackLangException(
                locale_key, fallback_language, file_path)


def localize(locale_key: str, language: str) -> str | None:
    if locale_key not in locales:
        logging.warning(
            f'No locales were found for {locale_key}. Please, review */locales/locales.json')
        return None

    available_languages = locales[locale_key]
    if language in available_languages:
        return available_languages[language]
    elif configuration['fallback_language'] in available_languages:
        return available_languages[configuration['fallback_language']]
    else:
        return None
