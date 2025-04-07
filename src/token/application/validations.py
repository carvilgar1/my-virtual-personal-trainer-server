
import re

from src.common.application import error_builders
from src.common.application.validations import BaseFormValidator, validate_email_format
from src.common.domain import Error, ErrorLocalizable, errors
from src.common.domain.user_credentials import (UserCredentials,
                                                UserCredentialsFormFields)
from src.constants import CommonErrorCodes, TokenErrorCodes

def __build_empty_user_id_error() -> Error:
    return ErrorLocalizable(CommonErrorCodes.MISSING_MANDATORY_FIELD, CommonErrorCodes.MISSING_MANDATORY_FIELD, 'The field is required')

class TokenFormValidator(BaseFormValidator):
    def __init__(self, user_credentials: UserCredentials):
        super.__init__()
        
        self.username = user_credentials.username
        self.email = user_credentials.email
        self.password = user_credentials.password

    def validate(self):
        self.validate_user_id()
        self.validate_password_field()

    def validate_password_field(self):
        if not self.password:
            error = self.build_empty_field_error()
            super._add_error(error)

            
    def validate_user_id(self):
        if self.username or self.email:
            if self.email:
                if not validate_email_format(self.email):
                    error = ErrorLocalizable(CommonErrorCodes.INVALID_EMAIL, CommonErrorCodes.INVALID_EMAIL, 'Email is invalid')
                    self.errors.add_error(error)
        else:
            error = ErrorLocalizable(TokenErrorCodes.MISSING_USER_IDENTIFIER, TokenErrorCodes.MISSING_USER_IDENTIFIER, 'Yo must introduce any user identification')
            self.errors = error
    
            