import sys
import yaml
import argparse
import logging
from logging.handlers import RotatingFileHandler
from signal import signal, SIGTERM

from bo.core.brain import Bo


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        dest="config", default=None,
                        help="path to the configuration file")
    parser.add_argument("-l", "--logfile",
                        dest="logfile", default=None,
                        help="the file to use for logging")
    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument("-q", "--quiet",
                        dest="loglevel", action="store_const",
                        const=logging.ERROR, default=logging.INFO,
                        help="set log level to ERROR")
    logging_group.add_argument("-d", "--debug",
                        dest="logLevel", action="store_const",
                        const=logging.DEBUG, default=logging.INFO,
                        help="set log level to DEBUG")
    args = parser.parse_args(args=args)

    rootLogger = logging.getLogger()
    if not args.logfile:
        loggerHandler = logging.StreamHandler(sys.stderr)
    else:
        loggerHandler = RotatingFileHandler(args.logfile, maxBytes=1024 * 1024)
    rootLogger.addHandler(loggerHandler)
    loggerFormatter = logging.Formatter(
            '[%(asctime)s] %(name)-8s %(levelname)-8s %(message)s')
    loggerHandler.setFormatter(loggerFormatter)
    rootLogger.setLevel(args.logLevel)
    logger = logging.getLogger('bo')

    if not args.config:
        args.config = 'conf/default.yaml'
    with open(args.config) as f:
        config = yaml.load(f.read())

    bo = None
    try:
        bo = Bo(logger=logger, config=config)

        def SIGTERM_handler(stack_frame):
            logger.info('Received SIGTERM')
            bo.close()
        signal(SIGTERM, lambda signum, frame: SIGTERM_handler(frame))
        bo.work_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception:
        logger.exception('Something went wrong')
        return 1
    finally:
        if bo:
            bo.close()

    return 0


if __name__ == '__main__':
    main(sys.argv[1:])
