from src.constants import (PASSWORD_ALLOWED_SYMBOLS, PASSWORD_MIN_LENGTH,
                           SignUpErrorCodes)

SIGN_UP_LOCALES = {
    'en': {
        SignUpErrorCodes.EMAIL_ALREADY_EXISTS: 'The email address you provided is already registered.',
        SignUpErrorCodes.PASSWORD_MISSING_DIGIT: 'Your password must contain at least one digit.',
        SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE: 'Your password must contain at least one lowercase letter.',
        SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR: f'Your password must contain at least one special character, such as {PASSWORD_ALLOWED_SYMBOLS}.',
        SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE: 'Your password must contain at least one uppercase letter.',
        SignUpErrorCodes.USER_ALREADY_REGISTERED: 'This user is already registered.',
        SignUpErrorCodes.USERNAME_ALREADY_EXISTS: 'The username you provided is already taken.',
        SignUpErrorCodes.PASSWORD_TOO_SHORT: f'Your password must be at least {PASSWORD_MIN_LENGTH} characters long.',
    },
    'es': {
        SignUpErrorCodes.EMAIL_ALREADY_EXISTS: 'La dirección de correo electrónico que proporcionó ya está registrada.',
        SignUpErrorCodes.PASSWORD_MISSING_DIGIT: 'Su contraseña debe contener al menos un dígito.',
        SignUpErrorCodes.PASSWORD_MISSING_LOWERCASE: 'Su contraseña debe contener al menos una letra minúscula.',
        SignUpErrorCodes.PASSWORD_MISSING_SPECIAL_CHAR: f'Su contraseña debe contener al menos un carácter especial, como {PASSWORD_ALLOWED_SYMBOLS}.',
        SignUpErrorCodes.PASSWORD_MISSING_UPPERCASE: 'Su contraseña debe contener al menos una letra mayúscula.',
        SignUpErrorCodes.USER_ALREADY_REGISTERED: 'Este usuario ya está registrado.',
        SignUpErrorCodes.USERNAME_ALREADY_EXISTS: 'El nombre de usuario que proporcionó ya está en uso.',
        SignUpErrorCodes.PASSWORD_TOO_SHORT: f'Su contraseña debe tener al menos {PASSWORD_MIN_LENGTH} caracteres.',
    },
}
