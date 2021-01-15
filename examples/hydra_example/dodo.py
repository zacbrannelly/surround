"""
This module defines the tasks that can be executed using `surround run [task name]`
"""

import os
import sys
import subprocess

from pathlib import Path

from testing.config import Config
from surround import load_config

CONFIG = load_config(name="config", config_class=Config)
DOIT_CONFIG = {'verbosity':2, 'backend':'sqlite3'}
PACKAGE_PATH = os.path.basename(CONFIG["package_path"])
IMAGE = "%s/%s:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
IMAGE_JUPYTER = "%s/%s-jupyter:%s" % (CONFIG["company"], CONFIG["image"], CONFIG["version"])
DOCKER_JUPYTER = "Dockerfile.Notebook"

PARAMS = [
    {
        'name': 'args',
        'long': 'args',
        'type': str,
        'default': ""
    }
]

def task_status():
    """Show information about the project such as available runners and assemblers"""
    return {
        'actions': ["%s -m %s status=1" % (sys.executable, PACKAGE_PATH)]
    }

def task_build():
    """Build the Docker image for the current project"""
    return {
        'actions': ['docker build --tag=%s .' % IMAGE],
        'params': PARAMS
    }

def task_remove():
    """Remove the Docker image for the current project"""
    return {
        'actions': ['docker rmi %s %s -f' % (IMAGE, IMAGE_JUPYTER)],
        'params': PARAMS
    }

def task_dev():
    """Run the main task for the project"""
    cmd = [
        "docker",
        "run",
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        "%s" % IMAGE,
        "python3 -m %s %s" % (PACKAGE_PATH, "%(args)s")
    ]
    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_interactive():
    """Run the Docker container in interactive mode"""
    def run():
        cmd = [
            'docker',
            'run',
            '-it',
            '--rm',
            '-w',
            '/app',
            '--volume',
            '%s/:/app' % CONFIG['volume_path'],
            IMAGE,
            'bash'
        ]
        process = subprocess.Popen(cmd, encoding='utf-8')
        process.wait()

    return {
        'actions': [run]
    }

def task_prod():
    """Run the main task inside a Docker container for use in production """
    return {
        'actions': ["docker run %s python3 -m %s %s" % (IMAGE, PACKAGE_PATH, "%(args)s")],
        'task_dep': ["build"],
        'params': PARAMS
    }

def task_train():
    """Run training mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    cmd = [
        "docker run",
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        IMAGE,
        "python3 -m testing mode=train %(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_batch():
    """Run batch mode inside the container"""
    output_path = CONFIG["volume_path"] + "/output"
    data_path = CONFIG["volume_path"] + "/input"

    cmd = [
        "docker run",
        "--volume \"%s\":/app/output" % output_path,
        "--volume \"%s\":/app/input" % data_path,
        IMAGE,
        "python3 -m testing mode=batch %(args)s"
    ]

    return {
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_train_local():
    """Run training mode locally"""
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "mode=train",
        "%(args)s"
    ]

    return {
        'basename': 'trainLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_batch_local():
    """Run batch mode locally"""
    cmd = [
        sys.executable,
        "-m %s" % PACKAGE_PATH,
        "mode=batch",
        "%(args)s"
    ]

    return {
        'basename': 'batchLocal',
        'actions': [" ".join(cmd)],
        'params': PARAMS
    }

def task_build_jupyter():
    """Build the Docker image for a Jupyter Lab notebook"""
    return {
        'basename': 'buildJupyter',
        'actions': ['docker build --tag=%s . -f %s' % (IMAGE_JUPYTER, DOCKER_JUPYTER)],
        'task_dep': ['build'],
        'params': PARAMS
    }

def task_jupyter():
    """Run a Jupyter Lab notebook"""
    cmd = [
        "docker",
        "run",
        "-itp",
        "8888:8888",
        '-w',
        '/app',
        "--volume",
        "\"%s/\":/app" % CONFIG["volume_path"],
        IMAGE_JUPYTER
    ]
    return {
        'actions': [" ".join(cmd)],
    }
