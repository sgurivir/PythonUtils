import logging

def prepare_logging(filename='/tmp/test.log'):
    """ Sets global logging configuration
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger().setLevel(logging.DEBUG)

    # Add file handler
    logger.addHandler(logging.FileHandler(filename).setFormatter(formatter))

    # Add stderr handler
    logger.addHandler(logging.StreamHandler().setFormatter(formatter))


def main():
  prepare_logging("/tmp/log.txt")
  logging.info("Test message")

if __name__ == '__main__':
  main()