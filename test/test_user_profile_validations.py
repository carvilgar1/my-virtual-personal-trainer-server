import unittest
from datetime import datetime, timedelta

from src.constants import (MAX_HEART_RATE, MAX_HEIGHT, MAX_WEIGHT,
                           MIN_HEART_RATE, MIN_HEIGHT, MIN_WEIGHT,
                           CommonErrorCodes, UserProfileErrorCodes)
from src.user_profile.application.validations import (
    SaveUserProfileFormValidator, UpdateUserProfileFormValidator)
from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfileFormKeys)


class TestUserProfileValidations(unittest.TestCase):
    def setUp(self):
        self.language = "en"
        self.valid_form = {
            UserProfileFormKeys.BIRTH_DATE: (datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d"),
            UserProfileFormKeys.HEIGHT: str((MIN_HEIGHT + MAX_HEIGHT) / 2),
            UserProfileFormKeys.WEIGHT: str((MIN_WEIGHT + MAX_WEIGHT) / 2),
            UserProfileFormKeys.MAX_HEART_RATE: str((MIN_HEART_RATE + MAX_HEART_RATE) // 2),
            UserProfileFormKeys.GENDER: Gender.MALE.name,
            UserProfileFormKeys.ACTIVITY_LEVEL: ActivityLevel.MODERATELY_ACTIVE.name,
        }

    def test_save_user_profile_validator_valid(self):
        validator = SaveUserProfileFormValidator(
            self.valid_form, self.language)
        validator.validate()
        self.assertEqual(validator._errors, [])
        self.assertEqual(validator.user_profile.gender, Gender.MALE)
        self.assertEqual(validator.user_profile.activity_level,
                         ActivityLevel.MODERATELY_ACTIVE)

    def test_save_user_profile_validator_missing_fields(self):
        validator = SaveUserProfileFormValidator({}, self.language)
        validator.validate()
        fields = [
            UserProfileFormKeys.BIRTH_DATE,
            UserProfileFormKeys.HEIGHT,
            UserProfileFormKeys.WEIGHT,
            UserProfileFormKeys.MAX_HEART_RATE,
            UserProfileFormKeys.GENDER,
            UserProfileFormKeys.ACTIVITY_LEVEL,
        ]
        error_fields = [e.validation_field for e in validator._errors]
        for field in fields:
            self.assertIn(field, error_fields)

    def test_save_user_profile_validator_invalid_gender(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.GENDER] = "INVALID"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.GENDER for e in validator._errors))

    def test_save_user_profile_validator_invalid_activity_level(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.ACTIVITY_LEVEL] = "INVALID"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.ACTIVITY_LEVEL for e in validator._errors))

    def test_save_user_profile_validator_invalid_height(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.HEIGHT] = str(MAX_HEIGHT + 10)
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))

    def test_save_user_profile_validator_invalid_weight(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.WEIGHT] = str(MIN_WEIGHT - 1)
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.WEIGHT for e in validator._errors))

    def test_save_user_profile_validator_invalid_max_heart_rate(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.MAX_HEART_RATE] = str(MAX_HEART_RATE + 1)
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.MAX_HEART_RATE for e in validator._errors))

    def test_save_user_profile_validator_invalid_birth_date(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.BIRTH_DATE] = (
            datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.BIRTH_DATE for e in validator._errors))

    def test_save_user_profile_validator_invalid_float_height(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.HEIGHT] = "not_a_float"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))

    def test_save_user_profile_validator_invalid_float_weight(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.WEIGHT] = "not_a_float"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.WEIGHT for e in validator._errors))

    def test_save_user_profile_validator_invalid_float_max_heart_rate(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.MAX_HEART_RATE] = "not_a_float"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.MAX_HEART_RATE for e in validator._errors))

    def test_save_user_profile_validator_invalid_date_birth_date(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.BIRTH_DATE] = "not_a_date"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.BIRTH_DATE for e in validator._errors))

    def test_update_user_profile_validator_partial_update(self):
        form = {
            UserProfileFormKeys.HEIGHT: str(MAX_HEIGHT + 10),
            UserProfileFormKeys.GENDER: Gender.FEMALE.name,
        }
        validator = UpdateUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))
        self.assertFalse(any(
            e.validation_field == UserProfileFormKeys.BIRTH_DATE for e in validator._errors))
        self.assertEqual(validator.user_profile.gender, Gender.FEMALE)

    def test_update_user_profile_validator_full_update(self):
        form = {
            UserProfileFormKeys.BIRTH_DATE: (datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d"),
            UserProfileFormKeys.HEIGHT: str((MIN_HEIGHT + MAX_HEIGHT) / 2),
            UserProfileFormKeys.WEIGHT: str((MIN_WEIGHT + MAX_WEIGHT) / 2),
            UserProfileFormKeys.MAX_HEART_RATE: str((MIN_HEART_RATE + MAX_HEART_RATE) // 2),
            UserProfileFormKeys.GENDER: Gender.FEMALE.name,
            UserProfileFormKeys.ACTIVITY_LEVEL: ActivityLevel.MODERATELY_ACTIVE.name,
        }
        validator = UpdateUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(validator.user_profile.is_completed())

    def test_save_user_profile_validator_none_values(self):
        form = {
            UserProfileFormKeys.BIRTH_DATE: None,
            UserProfileFormKeys.HEIGHT: None,
            UserProfileFormKeys.WEIGHT: None,
            UserProfileFormKeys.MAX_HEART_RATE: None,
            UserProfileFormKeys.GENDER: None,
            UserProfileFormKeys.ACTIVITY_LEVEL: None,
        }
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(len(validator._errors) >= 6)

    def test_save_user_profile_validator_empty_strings(self):
        form = {
            UserProfileFormKeys.BIRTH_DATE: "",
            UserProfileFormKeys.HEIGHT: "",
            UserProfileFormKeys.WEIGHT: "",
            UserProfileFormKeys.MAX_HEART_RATE: "",
            UserProfileFormKeys.GENDER: "",
            UserProfileFormKeys.ACTIVITY_LEVEL: "",
        }
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(len(validator._errors) >= 6)

    def test_save_user_profile_validator_injection_strings(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.BIRTH_DATE] = "'; DROP TABLE users; --"
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.BIRTH_DATE for e in validator._errors))

    def test_save_user_profile_validator_large_numbers(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.HEIGHT] = str(1e10)
        form[UserProfileFormKeys.WEIGHT] = str(1e10)
        form[UserProfileFormKeys.MAX_HEART_RATE] = str(1e10)
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.WEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.MAX_HEART_RATE for e in validator._errors))

    def test_save_user_profile_validator_negative_numbers(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.HEIGHT] = str(-100)
        form[UserProfileFormKeys.WEIGHT] = str(-50)
        form[UserProfileFormKeys.MAX_HEART_RATE] = str(-10)
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.WEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.MAX_HEART_RATE for e in validator._errors))

    def test_save_user_profile_validator_invalid_types(self):
        form = self.valid_form.copy()
        form[UserProfileFormKeys.HEIGHT] = []
        form[UserProfileFormKeys.WEIGHT] = {}
        form[UserProfileFormKeys.MAX_HEART_RATE] = []
        validator = SaveUserProfileFormValidator(form, self.language)
        validator.validate()
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.HEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.WEIGHT for e in validator._errors))
        self.assertTrue(any(e.validation_field ==
                        UserProfileFormKeys.MAX_HEART_RATE for e in validator._errors))


if __name__ == "__main__":
    unittest.main()
