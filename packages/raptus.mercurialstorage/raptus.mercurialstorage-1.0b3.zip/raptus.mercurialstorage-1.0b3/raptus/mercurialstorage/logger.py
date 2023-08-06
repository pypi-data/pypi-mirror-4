import os, time

from App.config import getConfiguration

class SVNLogger(object):
    
    def __init__(self, name):
        self.name = name
        config = getConfiguration()
        self.filename = os.path.join(os.path.dirname(config.eventlog.handler_factories[0].section.path), 'mercurial.log')
    
    def info(self, msg):
        file = open(self.filename, 'a')
        print >> file, ' '.join((time.strftime("%Y-%m-%d %H:%M:%S"), self.name, msg))
        file.close()

svn_logger = {}

def getLogger(name):
    global svn_logger
    if not svn_logger.has_key(name):
        svn_logger[name] = SVNLogger(name)
    return svn_logger[name]
    