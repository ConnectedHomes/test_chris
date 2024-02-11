"""Logging Configuration Function"""

import logging

bcolors = {
    'HEADER': '\033[95m',
    'OKBLUE': '\033[94m',
    'OKCYAN': '\033[96m',
    'OKGREEN': '\033[92m',
    'DARKGREEN': '\033[0;32m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

def configure_logger(logger_name: str, prepend_emoji = '', color = 'ENDC') -> None:
    # ://docs.python.org/3/library/logging.html

    # Create logger and define INFO as the log level https://docs.python.org/3/library/logging.html#levels
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Define our logging formatter
    formatter = logging.Formatter(
        f'{prepend_emoji} {bcolors["OKBLUE"]} %(levelname)s | %(name)s.py | Line %(lineno)d | {bcolors[color]} %(message)s {bcolors["ENDC"]}'
    )

    # Create our stream handler and apply the formatting
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Add the stream handler to the logger
    logger.addHandler(stream_handler)

    return logger
