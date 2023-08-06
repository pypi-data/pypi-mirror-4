import hooover
import logging
from time import sleep

session = hooover.LogglySession('hoovertest', 'hoover', 'b34v3r5')
i = session.get_input_by_name('sysloginput2')
handler = i.get_handler()
logger = logging.getLogger('syslogtologgly')
logger.addHandler(handler)
handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.info('this will go straight to loggly')

sleep(10)

print i.search(starttime='NOW-2MINUTES')
