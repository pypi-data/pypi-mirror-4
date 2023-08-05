import sys, logging

from fabric.state import env as _env

class Logger(object):
    def __init__(self, logger_name):
        self.logger_name = logger_name
        self.logger = logging.getLogger(self.logger_name)

    def debug(self, msg, *args, **kwargs):
        if _env.use_logging:
            self.logger.debug(msg, *args, **kwargs)
        else:
            print(msg)

    def info(self, msg, *args, **kwargs):
        if _env.use_logging:
            self.logger.info(msg, *args, **kwargs)
        else:
            print(msg)

    def warning(self, msg, stderr=False, *args, **kwargs):
        if _env.use_logging:
            self.logger.warning(msg, *args, **kwargs)
        else:
            if stderr:
                print >> sys.stderr, msg
            else:
                print(msg)

    def error(self, msg, *args, **kwargs):
        if _env.use_logging:
            self.logger.error(msg, *args, **kwargs)
        else:
            print(msg)

    def exception(self, msg, *args):
        if _env.use_logging:
            self.logger.exception(msg, *args)
        else:
            print(msg)

    def critical(self, msg, *args, **kwargs):
        if _env.use_logging:
            self.logger.critical(msg, *args, **kwargs)
        else:
            print(msg)

system_log = Logger('fabric')
stdout_log = Logger('fabric.stdout')
stderr_log = Logger('fabric.stderr')
