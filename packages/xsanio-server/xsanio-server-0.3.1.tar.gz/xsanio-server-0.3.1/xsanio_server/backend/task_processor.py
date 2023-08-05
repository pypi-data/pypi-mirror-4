#!/usr/bin/env python
from __future__ import absolute_import
import cronclient_common
import logging
import pickle
import subprocess
import datetime
import multiprocessing
import Queue
import time


LOGGER = logging.getLogger(__name__)
SHELL = '/bin/sh'
QUEUE_REFRESH_INTERVAL = 0.05
REPORT_INTERVAL = 5.0


class task_processor(object):
    """Runs shell commands,
    Processes the results,
    Pushes the results into results queue

    """
    TASK_QUEUE = None
    RESULT_QUEUE = None

    def  __init__(self, _task_queue, _result_queue):
        """Set up the object with two internal queues:
        TASK_QUEUE -- we grab new tasks from this one and then run commands
        RESULT_QUEUE -- dump tasks results here. 

        """
        self.TASK_QUEUE = _task_queue
        self.RESULT_QUEUE = _result_queue

    def process_message(self, message):
        """Interpret the pickle message
        Run appropriate command

        """
        task = pickle.loads(message, )
        task_type = task['task_type']
        task_results_queue = multiprocessing.Queue()
        task_result = {}

        LOGGER.info("Processing message")

        if task_type == 'run_cmd':
            task_command = task['task_command']

            def run_task(self):
                """Since we want to update the task status while it's running,
                let's launch it in a forked manner. 
                After the process finishes, the result will be added to 
                parent's function queue (task_results_queue)
                Obviously, there'll be only one item in that queue

                """
                result = {}
                try:
                    cmd_result = self.run_command(task_command).strip()
                    LOGGER.info("Command output: %s", cmd_result)
                    result = {
                        'task': task,
                        'status': 'COMPLETE',
                        'output': cmd_result,
                        'code': 0}

                except subprocess.CalledProcessError as e:
                    LOGGER.info(
                        "Command exited with status %s and output: %s",
                        e.returncode,
                        e.output.strip())
                    result = {
                        'task': task,
                        'status': 'ERROR',
                        'output': e.output.strip(),
                        'code': e.returncode}

                task_results_queue.put(result)

            cmd_process = multiprocessing.Process(
                target=run_task,
                args=(self, ))

            cmd_process.start()
            while True:
                try:
                    task_result = task_results_queue.get(True, 0.05)
                    break
                except Queue.Empty:
                    LOGGER.info("Task %s is running", task_command)
                    self.update_task_status(
                        task,
                        'RUNNING',
                        None,
                        0)

                    #   Join the process to avoid high CPU usage
                    cmd_process.join(REPORT_INTERVAL)
                    pass

            self.update_task_status(
                task_result['task'],
                task_result['status'],
                task_result['output'],
                task_result['code'])

        else:
            LOGGER.info("Unknown task type: %s", task_type)

    def update_task_status(self, task, status, output, code):
        """Pushes the task status into RESULT_QUEUE
        The RESULT_QUEUE is processed by publisher thread 

        """
        result = {
            'job_id': task['job_id'],
            'task_id': task['task_id'],
            'timestamp':  datetime.datetime.now(),
            'status': status,
            'output': output,
            'code': code,
        }

        self.RESULT_QUEUE.put(pickle.dumps(result))

    def run_command(self, cmd):
        """Small wrapper around subprocess call

        """
        return subprocess.check_output(
            [SHELL, '-c', cmd], 
            stderr=subprocess.STDOUT)

    def run(self):
        """Watches TASK_QUEUE for changes.
        When a new task is added, process it in the background by
        spawning the process_message function in forked manner

        """
        LOGGER.info("Task processor launched")

        while True:
            try:
                message = self.TASK_QUEUE.get(True, QUEUE_REFRESH_INTERVAL)
                LOGGER.info("Sending message for processing")
                multiprocessing.Process(
                    target=self.process_message,
                    args=(message, )).start()
            except Queue.Empty:
                continue
