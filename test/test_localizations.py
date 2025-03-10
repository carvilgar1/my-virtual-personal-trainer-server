import unittest
from unittest.mock import MagicMock

from src.common.application.localizations import (ErrorLocalizable,
                                                  LocalesAggregator,
                                                  LocalesNotLoadedError,
                                                  Localizer,
                                                  ResponseLocalizable)
from src.common.domain.response import Error, Response, Status


class LocalesAggregatorTests(unittest.TestCase):

    def setUp(self):
        self.locales_aggregator = LocalesAggregator()
        self.sample_locales = {
            'en': {'greeting': 'Hello', 'farewell': 'Goodbye'},
            'es': {'greeting': 'Hola', 'farewell': 'Adiós'}
        }

    def test_add_locales(self):
        self.locales_aggregator.add_locales(self.sample_locales)
        self.assertTrue(self.locales_aggregator._LocalesAggregator__loaded)
        self.assertEqual(
            self.locales_aggregator._LocalesAggregator__application_locales['en']['greeting'], 'Hello')
        self.assertEqual(
            self.locales_aggregator._LocalesAggregator__application_locales['es']['farewell'], 'Adiós')

    def test_application_locales_not_loaded(self):
        with self.assertRaises(LocalesNotLoadedError):
            _ = self.locales_aggregator.application_locales

    def test_application_locales_loaded(self):
        self.locales_aggregator.add_locales(self.sample_locales)
        self.assertEqual(
            self.locales_aggregator.application_locales['en']['greeting'], 'Hello')
        self.assertEqual(
            self.locales_aggregator.application_locales['es']['farewell'], 'Adiós')

    def test_combine_locales(self):
        locales_part1 = {
            'en': {'greeting': 'Hello'},
            'fr': {'greeting': 'Bonjour'}
        }
        locales_part2 = {
            'en': {'farewell': 'Goodbye'},
            'es': {'greeting': 'Hola'}
        }
        self.locales_aggregator.add_locales(locales_part1)
        self.locales_aggregator.add_locales(locales_part2)
        self.assertEqual(
            len(self.locales_aggregator.application_locales['en']), 2)
        self.assertEqual(
            len(self.locales_aggregator.application_locales['fr']), 1)
        self.assertEqual(
            len(self.locales_aggregator.application_locales['es']), 1)


class LocalizerTests(unittest.TestCase):

    def setUp(self):
        self.sample_locales = {
            'en': {'greeting': 'Hello', 'farewell': 'Goodbye'},
            'es': {'greeting': 'Hola', 'farewell': 'Adiós'}
        }
        self.localizer = Localizer(self.sample_locales)

    def test_localize_error_message(self):
        error = ErrorLocalizable('404', 'greeting', 'Not Found')
        self.localizer.localize(error, 'en')
        self.assertEqual(error.message, 'Hello')

    def test_localize_error_message_with_fallback(self):
        error = ErrorLocalizable('404', 'greeting', 'Not Found')
        self.localizer.localize(error, 'fr')
        self.assertEqual(error.message, 'Hello')

    def test_localize_error_message_with_unknown_locale_id(self):
        error = ErrorLocalizable('404', 'unknown_key', 'Not Found')
        self.localizer.localize(error, 'en')
        self.assertEqual(error.message, 'Not Found')

    def test_localize_error_with_default_when_missing_locale(self):
        sample_locales = {'en': {'farewell': 'Goodbye'}}
        localizer = Localizer(sample_locales)
        error = ErrorLocalizable('404', 'greeting', 'Default message')
        localizer.localize(error, 'fr')
        self.assertEqual(error.message, 'Default message')

    def test_localize_nested_errors(self):
        parent_error = ErrorLocalizable(
            '100', 'greeting', default_message='Parent default')
        child_error1 = ErrorLocalizable(
            '101', 'farewell', default_message='Child1 default')
        child_error2 = ErrorLocalizable(
            '102', 'greeting', default_message='Child2 default')
        child_error3 = ErrorLocalizable(
            '102', 'unknown_key', default_message='Child3 default')
        child_error4 = Error(
            '102', 'Native error message', 'validation_field')
        parent_error.add_error(child_error1)
        parent_error.add_error(child_error2)
        child_error2.add_error(child_error3)
        child_error2.add_error(child_error4)
        self.localizer.localize(parent_error, 'en')
        self.assertEqual(parent_error.message, 'Hello')
        self.assertEqual(child_error1.message, 'Goodbye')
        self.assertEqual(child_error2.message, 'Hello')
        self.assertEqual(child_error3.message, 'Child3 default')
        self.assertEqual(child_error4.message, 'Native error message')

    def test_localize_response(self):
        error = ErrorLocalizable('404', 'greeting', 'Not Found')
        response = ResponseLocalizable(Status.ERROR, error)
        self.localizer.localize(response, 'en')
        self.assertEqual(response.error.message, 'Hello')


if __name__ == '__main__':
    unittest.main()
