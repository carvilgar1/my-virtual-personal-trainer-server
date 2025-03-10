import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Iterator

from src.common.domain import Error, Response
from src.common.domain.response import Status
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


class ErrorMessageLocalization(LocalizableProperty):
    def __init__(self, locale_id: str, error: Error):
        self.locale_id = locale_id
        self.error = error

    def get_loacale_id(self) -> str:
        return self.locale_id

    def localize(self, text: str) -> None:
        self.error.message = text


class ErrorLocalizable(Error, LocalizableType):
    def __init__(self, code: str, message_locale_id: str, default_message: str = None, validation_field: str = None, errors: list['Error'] = None):
        super().__init__(code, default_message, validation_field, errors)
        self.error_message_localization = ErrorMessageLocalization(
            message_locale_id, self)

    def get_localizable_properties(self) -> Iterator[LocalizableProperty]:
        yield self.error_message_localization
        if self.errors:
            yield from self.__get_nested_localizable_properties()

    def __get_nested_localizable_properties(self) -> Iterator[LocalizableProperty]:
        for nested_error in self.errors:
            if isinstance(nested_error, LocalizableType):
                for localizable_property in nested_error.get_localizable_properties():
                    yield localizable_property


class ResponseLocalizable(Response, LocalizableType):
    def __init__(self, status: Status, error: Error = None):
        super().__init__(status, error)

    def get_localizable_properties(self) -> Iterator[LocalizableProperty]:
        if self.error and isinstance(self.error, LocalizableType):
            yield from self.error.get_localizable_properties()


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
