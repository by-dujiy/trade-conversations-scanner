import os
import logging
import inspect
import requests
import dotenv


dotenv.load_dotenv()

# for notification in telegram, if exception occur
DEV_TG = os.getenv('DEV_TG')
OWNER_TG = os.getenv("OWNER_TG")


error_logger = logging.getLogger('exceptions_log')
fh = logging.FileHandler('error.log')
fh.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
    )
)
error_logger.addHandler(fh)
error_logger.setLevel(logging.WARNING)


debug_logger = logging.getLogger('debug_logger')
stream_log = logging.StreamHandler()
stream_log.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
    )
)
debug_logger.addHandler(stream_log)
debug_logger.setLevel(logging.DEBUG)


def exc_log(e):
    """
    Log exception (show in cli panel and write in file)
    Send error notification via telegram - to developer and owner
    :param e: exception message
    :return:
    """
    caller_function_name = inspect.stack()[1].function
    message = f"[{caller_function_name}] occur exception: {e}"
    error_logger.error(message, exc_info=True)
    requests.get(DEV_TG)
    requests.get(OWNER_TG)


def debug_log(msg='start'):
    caller_function_name = inspect.stack()[1].function
    message = f"[{caller_function_name}]: {msg}"
    debug_logger.info(message)
