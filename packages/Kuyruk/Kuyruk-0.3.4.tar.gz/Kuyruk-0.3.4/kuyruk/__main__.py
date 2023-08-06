import imp
import logging
import logging.config
import optparse

from kuyruk import Kuyruk

logger = logging.getLogger(__name__)


def main():
    parser = optparse.OptionParser()
    parser.add_option('--config')
    parser.add_option('--logging-config')
    parser.add_option('--logging-level', default='INFO')
    # These options below override the options from config module
    parser.add_option('--queues')
    parser.add_option('--max-load', type='int')
    parser.add_option('--max-run-time', type='int')
    parser.add_option('--save-failed-tasks', action='store_true')
    options, args = parser.parse_args()

    if options.config:
        config = imp.load_source('config', options.config)
    else:
        config = imp.new_module('config')

    if options.logging_config:
        logging.config.fileConfig(options.logging_config)
    else:
        logging.getLogger('pika').level = logging.WARNING
        level = getattr(logging, options.logging_level)
        logging.basicConfig(level=level)

    if options.max_load is not None:
        config.KUYRUK_MAX_LOAD = options.max_load

    if options.max_run_time is not None:
        config.KUYRUK_MAX_RUN_TIME = options.max_run_time

    if options.save_failed_tasks:
        config.KUYRUK_SAVE_FAILED_TASKS = options.save_failed_tasks

    Kuyruk(config).run(options.queues)

if __name__ == '__main__':
    main()
