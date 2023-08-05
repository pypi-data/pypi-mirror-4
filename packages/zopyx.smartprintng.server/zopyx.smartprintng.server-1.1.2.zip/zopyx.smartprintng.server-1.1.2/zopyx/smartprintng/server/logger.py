##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import logging
import logging.handlers

def getLogger(filename=None, level='INFO'):

    if not filename:
        raise RuntimeError('getLogger(): no argument for "filename" given')

    logger = logging.getLogger() 
    hdlr = logging.handlers.TimedRotatingFileHandler(filename, when='midnight', backupCount=30) 
    formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s', '%d.%m.%y %H:%M:%S')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(getattr(logging, level))
    return logger

LOG = getLogger('smartprintng.log')
