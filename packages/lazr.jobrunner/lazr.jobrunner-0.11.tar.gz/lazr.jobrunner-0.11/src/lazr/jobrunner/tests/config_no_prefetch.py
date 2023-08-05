BROKER_VHOST = "/"
CELERY_RESULT_BACKEND = "amqp"
CELERY_IMPORTS = ("lazr.jobrunner.tests.test_celerytask", )
CELERYD_CONCURRENCY = 1
import os
import oops
CELERY_ANNOTATIONS = {
    "run_file_job": {"file_job_dir": os.environ['FILE_JOB_DIR'],
                     'oops_config': oops.Config()}
    }
# Do not prefetch job data.
# See http://ask.github.com/celery/userguide/optimizing.html
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_ACKS_LATE = True
