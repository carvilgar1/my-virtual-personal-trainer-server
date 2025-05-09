import json
import os
import re
import tempfile
import unittest

from src.common.application.localizations import (LostFallbackLangException,
                                                  PlaceHolderReplacer,
                                                  configuration, load_locales,
                                                  locales, localize)


class TestLocalizations(unittest.TestCase):

    def setUp(self):
        locales.clear()

    def test_load_locales_with_tempfile(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"app_name": "MyApp"})
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "locales.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(
                    r'{"greeting": {"en": "Hello {{app_name}}", "es": "Hola {{app_name}}"}}')
            load_locales(temp_dir, replacer)
            self.assertIn("greeting", locales)
            self.assertIn("en", locales["greeting"])
            self.assertEqual(locales["greeting"]["en"], "Hello MyApp")

    def test_load_locales_no_fallback_lang_raises_exception(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "locales.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(r'{"greeting": {"es": "Hola"}}')
            self.assertRaises(LostFallbackLangException,
                              load_locales, temp_dir, {})

    def test_load_locales_with_null_placeholders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "locales.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(
                    r'{"greeting": {"en": "Hello {{app_name}}", "es": "Hola {{app_name}}"}}')
            load_locales(temp_dir)
            self.assertIn("greeting", locales)
            self.assertIn("en", locales["greeting"])
            self.assertEqual(locales["greeting"]["en"], r"Hello {{app_name}}")

    def test_load_locales_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "locales.json")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("not a json")
            with self.assertRaises(json.JSONDecodeError):
                load_locales(temp_dir)

    def test_localize_existing_key_and_language(self):
        locales.update({
            "greeting": {"en": "Hello", "es": "Hola"}
        })
        result = localize("greeting", "en")
        self.assertEqual(result, "Hello")

    def test_localize_fallback_language(self):
        locales.update({
            "greeting": {"es": "Hola", configuration["fallback_language"]: "Some"}
        })
        result = localize("greeting", "it")
        self.assertEqual(locales["greeting"]
                         [configuration["fallback_language"]], result)

    def test_localize_null_with_missing_fallback_language(self):
        locales.update({
            "greeting": {"es": "Hola"}
        })
        result = localize("greeting", "it")
        self.assertIsNone(result)

    def test_localize_missing_key(self):
        locales.clear()
        result = localize("nonexistent_key", "en")
        self.assertIsNone(result)

    def test_single_placeholder_replacement(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"name": "World"})
        input_str = "Hello {{name}}"
        result = replacer.replace(input_str)
        self.assertEqual(result, "Hello World")

    def test_no_replacement_when_key_missing(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"name": "World"})
        input_str = "Hello {{username}}"
        result = replacer.replace(input_str)
        self.assertEqual(result, "Hello {{username}}")

    def test_multiple_placeholder_replacements(self):
        replacer = PlaceHolderReplacer(
            r'{{(\w+)}}', {"name": "Alice", "city": "Wonderland"})
        input_str = "My name is {{name}} and I live in {{city}}."
        result = replacer.replace(input_str)
        self.assertEqual(result, "My name is Alice and I live in Wonderland.")

    def test_no_placeholder_in_string(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"name": "Alice"})
        input_str = "No placeholders here!"
        result = replacer.replace(input_str)
        self.assertEqual(result, input_str)

    def test_empty_string(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"name": "Alice"})
        input_str = ""
        result = replacer.replace(input_str)
        self.assertEqual(result, "")

    def test_placeholder_with_empty_replacement(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"name": ""})
        input_str = "Hello {{name}}, welcome!"
        result = replacer.replace(input_str)
        self.assertEqual(result, "Hello , welcome!")

    def test_placeholder_with_dynamic_placeholder(self):
        # Dinamic placeholders should be replaced by the application at real time using string format
        replacer = PlaceHolderReplacer(
            r'{{(\w+)}}', {"final_placeholder": "Some Final"})
        input_str = "Hello {{final_placeholder}}, welcome {dynamic_placeholder}!"
        result = replacer.replace(input_str)
        self.assertIn("Some Final", result)
        self.assertIn("{dynamic_placeholder}", result)
        self.assertEqual(
            result, "Hello Some Final, welcome {dynamic_placeholder}!")

    def test_replacer_with_repeated_placeholder(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"item": "apple"})
        input_str = "I like {{item}}, {{item}}, and {{item}}."
        result = replacer.replace(input_str)
        self.assertEqual(result, "I like apple, apple, and apple.")

    def test_replacer_with_empty_dict(self):
        # With no replacement dictionary, the original string should be unchanged.
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {})
        input_str = "Nothing changes: {{key}} remains."
        result = replacer.replace(input_str)
        self.assertEqual(result, "Nothing changes: {{key}} remains.")

    def test_replacer_with_non_string_input(self):
        replacer = PlaceHolderReplacer(r'{{(\w+)}}', {"number": "100"})
        # Passing a non-string input should raise a TypeError as re.sub expects a string.
        with self.assertRaises(TypeError):
            replacer.replace(12345)

    def test_replacer_invalid_regex(self):
        # An invalid regex should raise a re.error upon construction.
        with self.assertRaises(re.error):
            PlaceHolderReplacer(r'{{(((\w+)', {"name": "test"})

    def test_load_locales_empty_directory(self):
        # Test that calling load_locales on an empty directory does not raise an exception.
        with tempfile.TemporaryDirectory() as temp_dir:
            load_locales(temp_dir)
            self.assertEqual(locales, {})


if __name__ == "__main__":
    unittest.main()
