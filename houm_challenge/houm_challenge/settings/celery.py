import environ
# Initialise default environment variables
env = environ.Env(
    # set casting, default value
)

environ.Env.read_env()

CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_CACHE_BACKEND = env('CELERY_CACHE_BACKEND')
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_ACCEPT_CONTENT = [env('CELERY_ACCEPT_CONTENT')]
CELERY_RESULT_SERIALIZER = env('CELERY_RESULT_SERIALIZER')
CELERY_TASK_SERIALIZER = env('CELERY_TASK_SERIALIZER')
CELERY_TIMEZONE = env('CELERY_TIMEZONE')
CELERY_TASK_TRACK_STARTED = env('CELERY_TASK_TRACK_STARTED')
CELERY_TASK_TIME_LIMIT = env('CELERY_TASK_TIME_LIMIT')
CACHES = {
    'default': {
        'BACKEND': env('CELERY_CACHES_BACKEND'),
        'LOCATION': env('CELERY_CACHES_LOCATION'),
    }
}