from src.constants import CommonErrorCodes

COMMON_LOCALES = {
    'en': {
        CommonErrorCodes.UNKNOWN_ERROR: 'An unknown error occurred, please contact customer support',
        CommonErrorCodes.MISSING_MANDATORY_FIELD: 'The field is required',
        CommonErrorCodes.INVALID_INTEGER: 'The field must be an integer',
        CommonErrorCodes.INVALID_FLOAT: 'The field must be a float',
        CommonErrorCodes.INVALID_DATE: 'The field must be a valid date, format yyyy-MM-dd is expected',
        CommonErrorCodes.INVALID_DATETIME: 'The field must be a valid datetime, format ISO8601 yyyy-MM-ddTHH:mm:ss.ffffff±hh:mm is expected',
        CommonErrorCodes.INVALID_EMAIL: 'The field must be a valid email address',
        CommonErrorCodes.FORM_CONTAINS_ERRORS: 'The form contains errors',
        CommonErrorCodes.DATE_MUST_BE_IN_PAST: 'The date must be in the past'
    },
    'es': {
        CommonErrorCodes.UNKNOWN_ERROR: 'Ocurrió un error desconocido, por favor contacte al soporte técnico',
        CommonErrorCodes.MISSING_MANDATORY_FIELD: 'El campo es requerido',
        CommonErrorCodes.INVALID_INTEGER: 'El campo debe ser un entero',
        CommonErrorCodes.INVALID_FLOAT: 'El campo debe ser un decimal',
        CommonErrorCodes.INVALID_DATE: 'El campo debe ser una fecha válida, el formato esperado es yyyy-MM-dd',
        CommonErrorCodes.INVALID_DATETIME: 'El campo debe ser una fecha y hora válida, el formato ISO8601 yyyy-MM-ddTHH:mm:ss.fffffff+hh:mm es esperado',
        CommonErrorCodes.INVALID_EMAIL: 'El campo debe ser una dirección de correo electrónico válida',
        CommonErrorCodes.FORM_CONTAINS_ERRORS: 'El formulario contiene errores',
        CommonErrorCodes.DATE_MUST_BE_IN_PAST: 'La fecha debe ser en el pasado'
    }
}
