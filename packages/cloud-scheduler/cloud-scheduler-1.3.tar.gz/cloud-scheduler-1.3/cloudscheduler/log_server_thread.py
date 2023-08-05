import cPickle
import SocketServer
import struct
import logging
import logging.config
# Logging Server
        sock_handler = logging.handlers.SocketHandler('localhost',
                            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        sock_handler.setFormatter(log_formatter)

        log.addHandler(sock_handler)
    log_serv = Logging()
    log_serv.start()
    log_serv.stop()
    log_serv.join()

class LogRecordStreamHandler(SocketServer.StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while 1:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack(">L", chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.handleLogRecord(record)

    def unPickle(self, data):
        return cPickle.loads(data)

    def handleLogRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger(name)
        # N.B. EVERY record gets logged. This is because Logger.handle
        # is normally called AFTER logger-level filtering. If you want
        # to do filtering, do it at the client end to save wasting
        # cycles and network bandwidth!
        logger.handle(record)

class LogRecordSocketReceiver(SocketServer.ThreadingTCPServer):
    """simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):
        SocketServer.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = False
        self.timeout = 1
        self.logname = 'cloudscheduler_tcp'

    def serve_until_stopped(self):
        import select
        abort = False
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort

class Logging(threading.Thread):
    """
    Logging - Runs a SocketServer to handle logging
    """

    def __init__(self):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self.tcpserver = LogRecordSocketReceiver()
        self.quit = False

    def stop(self):
        log.debug("Waiting for logging loop to end")
        self.quit = True
        self.tcpserver.abort = True

    def run(self):
        if config.log_location:
            file_handler = None
            if config.log_max_size:
                file_handler = logging.handlers.RotatingFileHandler(
                                                config.log_location+'.tcp',
                                                maxBytes=config.log_max_size)
            else:
                try:
                    file_handler = logging.handlers.WatchedFileHandler(
                                                config.log_location+'.tcp',)
                except AttributeError:
                    # Python 2.5 doesn't support WatchedFileHandler
                    file_handler = logging.handlers.RotatingFileHandler(
                                                config.log_location+'.tcp',)

            logt = logging.getLogger('cloudscheduler_tcp')
            logt.setLevel(utilities.LEVELS[config.log_level])
            log_formatter = logging.Formatter(config.log_format)

            file_handler.setFormatter(log_formatter)
            logt.addHandler(file_handler)

        self.tcpserver.serve_until_stopped()