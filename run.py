import src
import time
import os


if __name__ == '__main__':
    while True:
        src.main_engine()
        src.debug_log('go sleep...')
        time.sleep(300)
        os.system('cls' if os.name == 'nt' else 'clear')
