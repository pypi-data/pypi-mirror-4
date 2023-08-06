import os
import signal
import logging
import traceback
import threading
import multiprocessing
from time import time, sleep

from setproctitle import setproctitle

from . import loader
from .queue import Queue
from .exceptions import Reject
from .connection import LazyConnection

logger = logging.getLogger(__name__)


class Worker(multiprocessing.Process):

    def __init__(self, queue_name, config):
        """
        :param queue_name: Queue name that this worker gets the messages from
        :param config: Configuration object
        """
        super(Worker, self).__init__()
        self.config = config
        self.connection = LazyConnection(
            self.config.RABBIT_HOST, self.config.RABBIT_PORT,
            self.config.RABBIT_USER, self.config.RABBIT_PASSWORD)
        self.channel = self.connection.channel()
        self.queue_name = queue_name
        is_local = queue_name.startswith('@')
        self.queue = Queue(queue_name, self.channel, local=is_local)

    def run(self):
        """Run worker until stop flag is set.

        Since Worker class is derived from multiprocessing.Process,
        it will be invoked when worker.start() is called.

        """
        setproctitle("kuyruk: worker on %s" % self.queue_name)
        self.start_wathcing_master()
        self.register_signals()
        self.started = time()
        self.queue.declare()
        self.channel.basic_qos(prefetch_count=1)
        # self.channel.tx_select()

        logger.info('Starting consume')
        for tag, task_description in self.queue:
            if self.should_quit():
                break
            self.on_task(tag, task_description)

        logger.debug("End run worker")

    def on_task(self, tag, task_description):
        logger.info('Task received: %s', task_description)
        if self.is_load_high():
            logger.warning('Load is high, rejecting task')
            self.queue.reject(tag)
            # self.channel.tx_commit()
            self.queue.pause(30)
        else:
            self.process_task(tag, task_description)
            # self.channel.tx_commit()

    def process_task(self, tag, task_description):
        try:
            self.import_and_call_task(task_description)
        # sleep() calls below prevent cpu burning
        except Reject:
            logger.warning('Task is rejected')
            sleep(1)
            self.queue.reject(tag)
        except Exception:
            logger.error('Task raised an exception')
            logger.error(traceback.format_exc())
            sleep(1)
            self.handle_exception(tag, task_description)
        else:
            logger.info('Task is successful')
            self.queue.ack(tag)

    def handle_exception(self, tag, task_description):
        retry_count = task_description.get('retry', 0)
        if retry_count:
            logger.debug('Retry count: %s', retry_count)
            self.queue.discard(tag)
            task_description['retry'] = retry_count - 1
            self.queue.send(task_description)
        else:
            logger.debug('No retry left')
            self.queue.discard(tag)
            if self.config.SAVE_FAILED_TASKS:
                self.save_failed_task(task_description)

    def save_failed_task(self, task_description):
        logger.info('Saving failed task')
        task_description['queue'] = self.queue_name
        failed_queue = Queue('kuyruk_failed', self.channel)
        failed_queue.send(task_description)
        logger.debug('Saved')

    def import_and_call_task(self, task_description):
        """Call task function.
        This is the method where user modules are loaded.

        """
        module, function, cls, object_id, args, kwargs = (
            task_description['module'],
            task_description['function'],
            task_description['class'],
            task_description['object_id'],
            task_description['args'],
            task_description['kwargs'])
        task, cls = loader.import_task(module, cls, function)

        if cls:
            obj = cls.get(object_id)
            if not obj:
                logger.warning("<%s.%s id=%r> is not found",
                               module, cls.__name__, object_id)
                return

            args = list(args)
            args.insert(0, obj)

        logger.debug('Task %r will be executed with args=%s and kwargs=%s',
                     task, args, kwargs)
        result = task.run(args, kwargs)
        logger.debug('Result: %r', result)

    def should_quit(self):
        def checks():
            CHECKS = [
                self.is_run_time_exceeded,
                self.is_master_dead,
            ]
            for check in CHECKS:
                yield check()
        return any(checks())

    def is_master_dead(self):
        try:
            os.kill(os.getppid(), 0)
        except OSError:
            return True

    def start_wathcing_master(self):
        """
        Start a Thread that watches the master and send itself SIGTERM
        when master is dead.

        """
        def watch():
            while True:
                if self.is_master_dead():
                    logger.critical('Master is dead')
                    # We do not call the handler directly here because
                    # pika is not thread safe.
                    os.kill(os.getpid(), signal.SIGTERM)
                    break
                else:
                    sleep(1)
        t = threading.Thread(target=watch)
        t.daemon = True
        t.start()

    def is_run_time_exceeded(self):
        if self.config.MAX_RUN_TIME is not None:
            passed_seconds = time() - self.started
            if passed_seconds >= self.config.MAX_RUN_TIME:
                logger.warning('Kuyruk run for %s seconds', passed_seconds)
                return True

    def is_load_high(self):
        return os.getloadavg()[0] > self.config.MAX_LOAD

    def register_signals(self):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, self.sigterm_handler)

    def sigterm_handler(self, signum, frame):
        logger.warning("Catched SIGTERM")
        logger.warning("Stopping %s...", self)
        self.queue.cancel()
