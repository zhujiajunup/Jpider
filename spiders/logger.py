import platform
import logging
import logging.config
import os

def logger_conf():
    """
    load basic logger configure
    :return: configured logger
    """

    if platform.system() == 'Windows':

        logging.config.fileConfig(os.path.abspath('../../')+'\\conf\\logging.conf')
    elif platform.system() == 'Linux':

        logging.config.fileConfig(os.path.abspath('../../')+'/conf/logging.conf')
    elif platform.system() == 'Darwin':
        print(os.path.abspath('../../'))
        logging.config.fileConfig(os.path.abspath('../../') + '/conf/logging.conf')
    logger = logging.getLogger('simpleLogger')

    return logger

LOGGER = logger_conf()