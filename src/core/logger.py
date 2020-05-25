import coloredlogs, logging

# disable logging for certain modules
loggers_to_disable = ['matplotlib', 'shapely.geos']

for logger_name in loggers_to_disable:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)

rootLogger = logging.getLogger('MSK')
coloredlogs.install(
    level='DEBUG',
    fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
)


def get_root_logger():
    return rootLogger


def get_child_logger(name):
    return rootLogger.getChild(name)
