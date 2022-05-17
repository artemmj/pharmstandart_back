# Swagger doc settings

SWAGGER_SETTINGS = {
    'DOC_EXPANSION': 'none',
    'SECURITY_DEFINITIONS': {
        'JWT': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'},
    },
}
