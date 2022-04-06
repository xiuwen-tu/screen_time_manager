import subprocess
import os
import time
import datetime
import logging
import win32gui
import win32con
import sys
import traceback
import threading
import keyboard    # 3rd-party module
import st_mngr_config

script_name = 'st_mngr'    # short for 'screen_time_manager'
script_ver = 0.06

top_list = []
win_list = []

logged_out = False


def register_logged_out():
    global logged_out
    logged_out = True


firefox_exe = r"C:\Program Files\Mozilla Firefox\firefox.exe"


def get_logger():
    logger = logging.getLogger('st_mngr')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('st_mngr.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


logger = get_logger()    # this global logger is used in main() and at the bottom


def enum_callback(hwnd, results):
	win_list.append((hwnd, win32gui.GetWindowText(hwnd)))


class TimingThread(threading.Thread):
    """Reports timing after allowed session time is up"""

    def __init__(self, name, start_time, session_minutes, daemon=True):
        """
        Initialize the thread
        As a 'daemon thread', at shutdown it will be stopped abruptly, not gracefully.
        """
        threading.Thread.__init__(self)
        self.name = name
        self.start_time = start_time
        self.session_minutes = session_minutes

    def run(self):
        """Run the thread"""
        while not logged_out:    # this while loop can exit when logged_out becomes True
            time.sleep(5)    # hard-coded 5 seconds to take less resource
            session_time = datetime.datetime.now() - self.start_time
            if session_time > datetime.timedelta(minutes = self.session_minutes + 1):
                self.session_minutes += 1
                print(f'\t{self.session_minutes} minute(s) passed...')

            
def main():
    global top_list, win_list, session_time, firefox_exe, url_list, logger

    print(os.getcwd())

    t0 = datetime.datetime.now()
    msg = f'\tOK. Program {script_name} ver {script_ver} started.'
    print(t0.strftime("%Y-%m-%d-%H:%M:%S"), msg)
    logger.info(msg)    # note some difference between t0 and logged time

    config = st_mngr_config.get_config(st_mngr_config.ini_filename)
    site_list = list(config['URL'].keys())

    print('\nHere are the selections:')
    for i,site in enumerate(site_list):
        print(f'\t{i}: \t{site}')
    user_input = input('Please select a site to visit:\n')
    site = site_list[int(user_input)]
    logger.info('\t' + site)
    url = config['URL'][site]
    session_time = int(config['Session_Time'][site])
    
    msg = f'Are {session_time} minutes sufficient? (Y/N)\n'
    user_input = input(msg)
    if user_input.upper() == 'Y':
        msg = f"Cool. We'll go for {session_time} minutes."
        print(msg)
        logger.info('\t' + msg)
    else:
        user_input = input('OK. How many minutes do you need?\n')
        session_time = int(user_input)
        msg = f'OK. Changed to {session_time} minute(s).'
        print(msg)
        logger.info('\t' + msg)
    print('\n')

    if site == 'jupyter-lab':
        os.chdir('D:\\')
        process = subprocess.Popen(url)    # url == 'jupyter-lab'
    else: 
        process = subprocess.Popen([firefox_exe, url])
    t1 = datetime.datetime.now()
    msg = f"\tOK. Firefox should be open."
    print(t1.strftime("%Y-%m-%d-%H:%M:%S"), msg)
    logger.info(msg)
    print('\nEnjoy!')

    if session_time == 0:    # for development use
        time.sleep(6)
        print('0 minute passed...')
    else:     
        for t in range(session_time):
            time.sleep(60)
            print(f'\t{t+1} minute(s) passed...')
    print('')

    t2 = datetime.datetime.now()
    msg = "\tOK. Time is up! Minimizing firefox..."
    print(t2.strftime("%Y-%m-%d-%H:%M:%S"), msg)
    logger.info(msg)
    
    win32gui.EnumWindows(enum_callback, top_list)
    firefox_list = [(hwnd, title) for hwnd, title in win_list if 'firefox' in title.lower()]
    if len(firefox_list) > 0:
        win32gui.ShowWindow(firefox_list[0][0], win32con.SW_MINIMIZE)
        print(f"OK. Firefox should have been minimized. Please log out.")
        timing_thread = TimingThread('Timing_Thread', t1, session_time)
        timing_thread.start()
        print('\nPress enter after logging out...\n')
        keyboard.on_press_key("enter", lambda _:register_logged_out())
        while not logged_out:    # this loop exits when enter is pressed
            time.sleep(0.5)    # hard-coded 0.5 second to be more responsive
    else:
        print('\nGood. You cosed Firefox already.\n')

    t3 = datetime.datetime.now()
    msg = f'\tActual session time:  {t3 - t1}'
    print(t3.strftime("%Y-%m-%d-%H:%M:%S"), msg)
    logger.info(msg)

    print('\nBye!')


if __name__ == "__main__":
    """ The following 'bare except' is not recommended, unless if we can log error info."""
    try:
        main()
    except:
        print('\nOops, something is wrong. Please check the last input, among other things...')
        msg = str(sys.exc_info()[0]) + "::  " + str(sys.exc_info()[1])
        print(msg)
        logger.error(msg)
        msg = traceback.extract_tb(sys.exc_info()[2])
        print(msg)
        logger.error(msg)
