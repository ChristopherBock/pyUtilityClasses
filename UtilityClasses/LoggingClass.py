__author__ = 'Christopher Bock'


class LoggingClass(object):
    """
    Serves as base class for classes implementing rudimentary logging functions. In case no logger is supplied to the
    constructor, the output will be printed to the console via the print function. If a logger is supplied it will have
    to implement a print_log function accepting three parameters:
     message                being the message to be shown
     msg_type               the type of the message
     suppress_timestamp     whether or not timestamps should be shown alongside with the message
    the parameters do not need to be named.
    """
    def __init__(self, logger=None):
        self.logger = logger
        return

    def print_line(self, msg_type='INFO', suppress_timestamp=False):
        self.print_log('-'*25, msg_type, suppress_timestamp)

    def print_log(self, message, msg_type='INFO', suppress_timestamp=False):
        if self.logger:
            self.logger.print_log(message, msg_type, suppress_timestamp)
        else:
            if suppress_timestamp:
                print("%s: %s" % (msg_type, message))
            else:
                import time

                print("%s-%s: %s" % (time.strftime("%y-%m-%d/%H:%M:%S"), msg_type, message))
        return
