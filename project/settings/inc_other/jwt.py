from datetime import timedelta

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(seconds=900000),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}
