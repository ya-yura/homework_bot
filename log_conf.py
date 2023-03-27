ERROR_LOG_FILENAME = '.bot-errors.log'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s, %(name)s, %(levelname)s, %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '%(message)s',
        },
    },
    'handlers': {
        'file_logger': {
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOG_FILENAME,
        },
        'main_logger': {
            'formatter': 'default',
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'homework': {
            'level': 'ERROR',
            'handlers': [
                'file_logger',
            ]
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'main_logger',
        ]
    },
}