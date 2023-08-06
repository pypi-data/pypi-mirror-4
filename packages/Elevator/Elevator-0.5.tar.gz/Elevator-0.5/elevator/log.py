# -*- coding:utf-8 -*-

# Copyright (c) 2012 theo crevon
#
# See the file LICENSE for copying permission.

import sys
import logging


def loglevel_from_str(log_level_str):
    log_level_str = log_level_str.upper()
    numeric_level = getattr(logging, log_level_str, None)

    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % log_level_str)

    return numeric_level


def setup_loggers(env):
    activity_log_file = env['global']['activity_log']
    errors_log_file = env['global']['errors_log']

    # Compute numeric log level value from string
    # ex: "DEBUG"
    log_level = loglevel_from_str(env['args']['log_level'])

    # Set up logging format and formatter instance
    log_format = "[%(asctime)s] %(levelname)s %(funcName)s : %(message)s"
    formatter = logging.Formatter(log_format)

    # Set up logging streams
    stdout_stream = logging.StreamHandler(sys.stdout)
    stdout_stream.setFormatter(formatter)
    activity_file_stream = logging.FileHandler(activity_log_file)
    activity_file_stream.setFormatter(formatter)
    errors_file_stream = logging.FileHandler(errors_log_file)
    errors_file_stream.setFormatter(formatter)

    # Set up activity logger
    activity_logger = logging.getLogger("activity_logger")
    activity_logger.setLevel(log_level)
    activity_logger.addHandler(activity_file_stream)
    activity_logger.addHandler(stdout_stream)

    # Setup up errors logger
    errors_logger = logging.getLogger("errors_logger")
    errors_logger.setLevel(logging.WARNING)
    errors_logger.addHandler(errors_file_stream)

    return activity_logger, errors_logger
