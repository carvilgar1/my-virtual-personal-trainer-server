import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

from src.constants import DEFAULT_LANGUAGE


class LocalesNotLoadedError(Exception):
    def __init__(self):
        super().__init__('No locales has been loaded')


class LocalesAggregator:
    def __init__(self):
        self.__loaded = False
        self.__application_locales = defaultdict(dict[str, dict[str, str]])

    def add_locales(self, locales: dict[str, dict[str, str]]) -> 'LocalesAggregator':
        for language, locale in locales.items():
            if language not in self.__application_locales:
                self.__application_locales[language] = {}
            self.__application_locales[language].update(locale)
        self.__loaded = True
        return self

    @property
    def application_locales(self) -> dict[str, dict[str, str]]:
        if not self.__loaded:
            raise LocalesNotLoadedError
        return self.__application_locales


class LocalizableProperty(ABC):
    @abstractmethod
    def get_loacale_id(self) -> str:
        pass

    @abstractmethod
    def localize(self, text: str) -> None:
        pass


class LocalizableType(ABC):
    @abstractmethod
    def get_localizable_properties(self) -> list[LocalizableProperty]:
        pass


class Localizer:
    def __init__(self, application_locales: dict[str, dict[str, str]]):
        self.__application_locales = application_locales

    def localize(self, obj: Any, language: str) -> None:
        if isinstance(obj, LocalizableType):
            for localizable_property in obj.get_localizable_properties():
                locale_id = localizable_property.get_loacale_id()
                localized_text = self.__application_locales.get(language, self.__application_locales[DEFAULT_LANGUAGE])\
                    .get(locale_id)

                if localized_text:
                    # overwite default message if exists
                    localizable_property.localize(localized_text)
                else:
                    logging.warning(
                        f'No localized text found for locale_id: {locale_id}')
