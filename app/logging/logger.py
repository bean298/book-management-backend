import logging
import os
import sys  # Write Log into console
from logging.handlers import (
    TimedRotatingFileHandler,
)  # Write Log into file with auto create new file Log in new date


def setup_logger(service_name: str, log_directory: str = "logs"):
    # Create file log if it doesnt exist yet
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Path to file log
    log_file_path = os.path.join(log_directory, "app.log")

    # Setting logger
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Format what information will show in file log
    formatLog = "[%(asctime)s], %(levelname)-8s [%(pathname)s :%(lineno)d in function %(funcName)s] %(message)s"  # noqa: E501

    # Handler auto create new file log in new date
    file_handler = TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,  # Keep 7 days log
    )
    file_handler.setFormatter(logging.Formatter(formatLog))

    # Handler write log into console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(formatLog))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger("book-management")
