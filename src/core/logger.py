import coloredlogs, logging

rootLogger = logging.getLogger()
coloredlogs.install(
  level='DEBUG',
  fmt='%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
)

def get_root_logger():
  return rootLogger

def get_child_logger(name):
  return rootLogger.getChild(name)
