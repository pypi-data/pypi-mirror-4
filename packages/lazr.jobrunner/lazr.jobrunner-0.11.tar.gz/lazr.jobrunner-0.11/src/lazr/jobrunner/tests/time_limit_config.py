BROKER_VHOST = "/"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("lazr.jobrunner.tests.test_celerytask", )
CELERYD_CONCURRENCY = 1
CELERYD_TASK_SOFT_TIME_LIMIT = 1
import os
import oops
CELERY_ANNOTATIONS = {
    "run_file_job": {"file_job_dir": os.environ['FILE_JOB_DIR'],
                     'oops_config': oops.Config()}
    }
