import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'PORT': 5432
    }
}
