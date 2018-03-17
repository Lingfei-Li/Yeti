import logging

FORMAT = '[%(levelname)s] %(name)s - %(message)s'


def get_logger(name="root"):
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
