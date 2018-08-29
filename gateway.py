import traceback

import listener
import buyer
from logger import setup_logger

logger = setup_logger('gateway')

if __name__ == '__main__':
    try:
        logger.debug(f"Start payment gateway. DEBUG mod.")
        listener.start()
        buyer.start()
    except:
        logger.error(f"Unhandled error! \n{traceback.format_exc()}")
    finally:
        logger.debug("Stop gateway.")
