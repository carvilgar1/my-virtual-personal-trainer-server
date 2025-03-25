from src.constants import TokenErrorCodes
from src.common.domain.user_credentials import UserCredentialsFormFields

TOKEN_LOCALES = {
    'en': {
        TokenErrorCodes.MISSING_USER_IDENTIFIER: f"Either '{UserCredentialsFormFields.USERNAME}' or '{UserCredentialsFormFields.EMAIL}' should be provided",
        TokenErrorCodes.INVALID_TOKEN: 'Invalid token',
        TokenErrorCodes.EXPIRED_TOKEN: 'Expired token',
    },
    'es': {
        TokenErrorCodes.MISSING_USER_IDENTIFIER: f"Se debe proporcionar '{UserCredentialsFormFields.USERNAME}' o '{UserCredentialsFormFields.EMAIL}'",
        TokenErrorCodes.INVALID_TOKEN: 'Token inválido',
        TokenErrorCodes.EXPIRED_TOKEN: 'Token expirado',
    },
}
