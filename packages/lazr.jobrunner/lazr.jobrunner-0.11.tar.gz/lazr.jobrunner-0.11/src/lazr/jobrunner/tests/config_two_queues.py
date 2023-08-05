BROKER_VHOST = "/"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("lazr.jobrunner.tests.test_celerytask", )
CELERYD_CONCURRENCY = 1
CELERY_QUEUES = {
    "standard": {"binding_key": "job.standard"},
    "standard_slow": {"binding_key": "job.standard.slow"},
    }
CELERY_DEFAULT_EXCHANGE = "standard"
CELERY_DEFAULT_QUEUE = "standard"
CELERY_CREATE_MISSING_QUEUES = False
import os
import oops
CELERY_ANNOTATIONS = {
    "run_file_job": {"file_job_dir": os.environ['FILE_JOB_DIR'],
                     'oops_config': oops.Config()}
    }
