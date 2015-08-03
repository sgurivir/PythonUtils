import logging


def config_root(name=__name__, level=logging.DEBUG, filename='/tmp/test.log'):
    """ Sets global logging configuration
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logging.getLogger(name).setLevel(level)

    # Add file handler
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logging.getLogger(name).addHandler(file_handler)

    # Add stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logging.getLogger(name).addHandler(stream_handler)

    return logging.getLogger(name)
