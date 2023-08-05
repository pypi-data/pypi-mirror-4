from simple_config import *
import os
import oops
CELERY_ANNOTATIONS = {
    "run_file_job": {"file_job_dir": os.environ['FILE_JOB_DIR'],
                     'oops_config': oops.Config()}
    }
