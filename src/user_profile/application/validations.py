from datetime import datetime

from src.common.application.error_builders import init_missing_field_error
from src.common.application.localizations import localize as _
from src.common.application.validations import (BaseFormValidator,
                                                validate_date, validate_float)
from src.common.domain import Error
from src.constants import (MAX_HEART_RATE, MAX_HEIGHT, MAX_WEIGHT,
                           MIN_HEART_RATE, MIN_HEIGHT, MIN_WEIGHT,
                           CommonErrorCodes, UserProfileErrorCodes)
from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfile,
                                                  UserProfileFormKeys)


class SaveUserProfileFormValidator(BaseFormValidator):
    gender_enum = ', '.join([gender.name for gender in Gender])
    activity_level_enum = ', '.join(
        [activity_level.name for activity_level in ActivityLevel])

    def __init__(self, form: dict, language: str):
        super().__init__(language)

        self.form = form
        self.user_profile = UserProfile()

    def validate(self) -> None:
        self.validate_birth_date()
        self.validate_height()
        self.validate_weight()
        self.validate_max_heart_rate()
        self.validate_gender()
        self.validate_activity_level()

    def validate_activity_level(self):
        activity_level = self.form.get(UserProfileFormKeys.ACTIVITY_LEVEL)
        if activity_level:
            try:
                activity_level = ActivityLevel[activity_level]
                self.user_profile.activity_level = activity_level
            except KeyError:
                message = _(CommonErrorCodes.INVALID_VALUE, self.language)
                if message:
                    message = message.format(
                        expected_values=self.activity_level_enum)
                error = Error(CommonErrorCodes.INVALID_VALUE,
                              message, UserProfileFormKeys.ACTIVITY_LEVEL)
                self._errors.append(error)
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.ACTIVITY_LEVEL, self.language)
            self._errors.append(error)

    def validate_gender(self):
        gender = self.form.get(UserProfileFormKeys.GENDER)
        if gender:
            try:
                gender = Gender[gender]
                self.user_profile.gender = gender
            except KeyError:
                message = _(CommonErrorCodes.INVALID_VALUE, self.language)
                if message:
                    message = message.format(expected_values=self.gender_enum)
                error = Error(CommonErrorCodes.INVALID_VALUE,
                              message, UserProfileFormKeys.GENDER)
                self._errors.append(error)
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.GENDER, self.language)
            self._errors.append(error)

    def validate_max_heart_rate(self):
        max_heart_rate = self.form.get(UserProfileFormKeys.MAX_HEART_RATE)
        if max_heart_rate:
            max_heart_rate, invalid_float_error = validate_float(
                max_heart_rate, self.language)
            if invalid_float_error:
                invalid_float_error.validation_field = UserProfileFormKeys.MAX_HEART_RATE
                self._errors.append(invalid_float_error)
            elif max_heart_rate < MIN_HEART_RATE or max_heart_rate > MAX_HEART_RATE:
                error = Error(UserProfileErrorCodes.INVALID_MAX_HEART_RATE, _(
                    UserProfileErrorCodes.INVALID_MAX_HEART_RATE, self.language), UserProfileFormKeys.MAX_HEART_RATE)
                self._errors.append(error)
            else:
                self.user_profile.max_heart_rate = max_heart_rate
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.MAX_HEART_RATE, self.language)
            self._errors.append(error)

    def validate_weight(self):
        weight = self.form.get(UserProfileFormKeys.WEIGHT)
        if weight:
            weight, invalid_float_error = validate_float(weight, self.language)
            if invalid_float_error:
                invalid_float_error.validation_field = UserProfileFormKeys.WEIGHT
                self._errors.append(invalid_float_error)
            elif weight < MIN_WEIGHT or weight > MAX_WEIGHT:
                error = Error(UserProfileErrorCodes.INVALID_WEIGHT, _(
                    UserProfileErrorCodes.INVALID_WEIGHT, self.language), UserProfileFormKeys.WEIGHT)
                self._errors.append(error)
            else:
                self.user_profile.weight = weight
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.WEIGHT, self.language)
            self._errors.append(error)

    def validate_height(self):
        height = self.form.get(UserProfileFormKeys.HEIGHT)
        if height:
            height, invalid_float_error = validate_float(height, self.language)
            if invalid_float_error:
                invalid_float_error.validation_field = UserProfileFormKeys.HEIGHT
                self._errors.append(invalid_float_error)
            elif height < MIN_HEIGHT or height > MAX_HEIGHT:
                error = Error(UserProfileErrorCodes.INVALID_HEIGHT, _(
                    UserProfileErrorCodes.INVALID_HEIGHT, self.language), UserProfileFormKeys.HEIGHT)
                self._errors.append(error)
            else:
                self.user_profile.height = height
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.HEIGHT, self.language)
            self._errors.append(error)

    def validate_birth_date(self):
        birth_date = self.form.get(UserProfileFormKeys.BIRTH_DATE)
        if birth_date:
            birth_date, invalid_date_error = validate_date(
                birth_date, self.language)
            if invalid_date_error:
                invalid_date_error.validation_field = UserProfileFormKeys.BIRTH_DATE
                self._errors.append(invalid_date_error)
            elif birth_date >= datetime.now():
                error = Error(CommonErrorCodes.DATE_MUST_BE_IN_PAST, _(
                    CommonErrorCodes.DATE_MUST_BE_IN_PAST, self.language), UserProfileFormKeys.BIRTH_DATE)
                self._errors.append(error)
            else:
                self.user_profile.birth_date = birth_date
        else:
            error = init_missing_field_error(
                UserProfileFormKeys.BIRTH_DATE, self.language)
            self._errors.append(error)


class UpdateUserProfileFormValidator(SaveUserProfileFormValidator):
    def __init__(self, form: dict, language: str):
        super().__init__(form, language)

    def validate(self) -> None:
        if UserProfileFormKeys.BIRTH_DATE in self.form:
            self.validate_birth_date()
        if UserProfileFormKeys.HEIGHT in self.form:
            self.validate_height()
        if UserProfileFormKeys.WEIGHT in self.form:
            self.validate_weight()
        if UserProfileFormKeys.MAX_HEART_RATE in self.form:
            self.validate_max_heart_rate()
        if UserProfileFormKeys.GENDER in self.form:
            self.validate_gender()
        if UserProfileFormKeys.ACTIVITY_LEVEL in self.form:
            self.validate_activity_level()
