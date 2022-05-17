CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'working_fs2_db': ('DB_TEST_NED', 'Использовать эту базу данных апи ФС2 для работы'),
    'taxi': ('test@test.test', 'Ссылка на сервис такси'),
    'delivery_serv': ('test@test.test', 'Ссылка на сервис доставки'),
    'booking': ('test@test.test', 'Ссылка на бронирование'),
}
CONSTANCE_CONFIG_FIELDSETS = {
    'Настройки': ('working_fs2_db',),
    'Статичные три ссылки на': ('taxi', 'delivery_serv', 'booking',)
}
