import logging, sys

LEVELS = {'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}

def getLogger(object):
    # logging.config.fileConfig(my_log_file)
    if isinstance(object,basestring):
        name = object
        # full filenames
        if '/myapp/' in name:
            name = 'myapp/' + name.split('/myapp/')[1]
        # path separators
        name = name.replace('/','.')
    elif type(object) is types.InstanceType:
        name = str(object.__class__)
    else:
        name = object.__class__.__module__ + '.' + object.__class__.__name__
    return logging.getLogger(name)

