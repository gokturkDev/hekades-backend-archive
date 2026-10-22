import sys


def configure_logger():
    import logging

    root = logging.getLogger()
    root.setLevel(logging.WARNING)
    uptrain_logger = logging.getLogger("uptrain")
    uptrain_logger.setLevel(logging.ERROR)

    # Create a unique logger for your application
    hekades_logger = logging.getLogger('hekades')
    hekades_logger.propagate = False

    # Set the logging level for your application
    hekades_logger.setLevel(logging.INFO)

    # Create a console handler with a specific level
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '🩺 HEKADES: %(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    hekades_logger.addHandler(handler)

    hekades_logger.info("Logger configured successfully!")
