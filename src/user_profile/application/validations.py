from src.common.application.error_builders import init_missing_field_error
from src.common.application.localizations import localize as _
from src.common.application.validations import (BaseFormValidator,
                                                validate_date, validate_float,
                                                validate_mandatory_field)
from src.common.domain import Error
from src.constants import CommonErrorCodes
from src.user_profile.domain.user_profile import (ActivityLevel, Gender,
                                                  UserProfileFormKeys)


class UserProfileFormValidator(BaseFormValidator):
    def __init__(self, form: dict, language: str):
        super().__init__(language)

        self.form = form
        self.user_profile = {}

    def _validate_date_of_birth(self) -> None:
        birth_date = self.form.get(UserProfileFormKeys.BIRTH_DATE)
        filled, error = validate_mandatory_field(
            birth_date, UserProfileFormKeys.BIRTH_DATE, self.language)
        if filled:
            valid_date, error = validate_date(birth_date, self.language)
            if valid_date:
                self.user_profile[UserProfileFormKeys.BIRTH_DATE] = valid_date
            else:
                self._errors.append(error)
        else:
            self._errors.append(error)

    def _validate_weight(self) -> None:
        self._validate_decimal_field(UserProfileFormKeys.WEIGHT)

    def _validate_height(self) -> None:
        self._validate_decimal_field(UserProfileFormKeys.HEIGHT)

    def _validate_max_heart_rate(self) -> None:
        self._validate_decimal_field(UserProfileFormKeys.MAX_HEART_RATE)

    def _validate_decimal_field(self, field_key: str) -> None:
        field_value = self.form.get(field_key, None)
        if field_value:
            field_value, errors = validate_float(
                field_value, self.language)
            if errors:
                self._errors.append(errors)
            else:
                self.user_profile[field_key] = field_value
        else:
            error = init_missing_field_error(field_key, self.language)
            self._errors.append(error)

    def _validate_gender(self) -> None:
        gender = self.form.get(UserProfileFormKeys.GENDER)
        filled, error = validate_mandatory_field(
            gender, UserProfileFormKeys.GENDER, self.language)
        if filled:
            try:
                gender = Gender[gender]
                self.user_profile[UserProfileFormKeys.GENDER] = gender
            except Exception:
                code = CommonErrorCodes.INVALID_VALUE
                mesesage = _(CommonErrorCodes.INVALID_VALUE, self.language)
                if mesesage:
                    mesesage = mesesage.format(
                        invalid_value=gender, valid_values=', '.join([x.name for x in Gender]))
                error = Error(code, mesesage)
                self._errors.append(error)
        else:
            self._errors.append(error)

    def _validate_activity_level(self) -> None:
        activity_level = self.form.get(UserProfileFormKeys.ACTIVITY_LEVEL)
        filled, error = validate_mandatory_field(
            activity_level, UserProfileFormKeys.ACTIVITY_LEVEL, self.language)
        if filled:
            try:
                activity_level = ActivityLevel[activity_level]
                self.user_profile[UserProfileFormKeys.ACTIVITY_LEVEL] = activity_level
            except Exception:
                code = CommonErrorCodes.INVALID_VALUE
                mesesage = _(CommonErrorCodes.INVALID_VALUE, self.language)
                if mesesage:
                    mesesage = mesesage.format(invalid_value=activity_level, valid_values=', '.join(
                        [x.name for x in ActivityLevel]))
                error = Error(code, mesesage)
                self._errors.append(error)
        else:
            self._errors.append(error)

    def validate(self) -> None:
        self._validate_date_of_birth()
        self._validate_weight()
        self._validate_height()
        self._validate_max_heart_rate()
        self._validate_gender()
        self._validate_activity_level()


class UserProfileUpdateFormValidator(UserProfileFormValidator):
    def __init__(self, form: dict, language: str):
        super().__init__(form, language)

    def validate(self) -> None:
        for key, _ in self.form.items():
            if key == UserProfileFormKeys.BIRTH_DATE:
                self._validate_date_of_birth()
            elif key == UserProfileFormKeys.WEIGHT:
                self._validate_weight()
            elif key == UserProfileFormKeys.HEIGHT:
                self._validate_height()
            elif key == UserProfileFormKeys.MAX_HEART_RATE:
                self._validate_max_heart_rate()
            elif key == UserProfileFormKeys.GENDER:
                self._validate_gender()
            elif key == UserProfileFormKeys.ACTIVITY_LEVEL:
                self._validate_activity_level()
