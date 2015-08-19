import time
from twitter_follow_bot import send_dm
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with open("dm_list", "r") as f:
    for line in f:
        try:
            message = "TeaCha Tea is offering company shares on RocketClub to the PH community. Find it here: http://producthunt.com"
            send_dm(line, message)
            time.sleep(20)
            logger.info("sending dm to {}: {}".format(str(line), str(message)))
            print("sending dm to {}: {}".format(str(line), str(message)))
        except Exception as e:
            logger.info("error: %s" % (str(e)))
            time.sleep(20)
            errorstring = '\"errors\":[{\"code\":150'
