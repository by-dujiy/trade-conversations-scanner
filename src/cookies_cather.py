from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from urllib.parse import urlparse
from .logger import debug_log, exc_log
import os
import time
import pickle
import dotenv

dotenv.load_dotenv()
FA_FILE = 'file.txt'


def checking_logout(driver):
    """
    Checking the current URL.
    If the session is logged out, start the logging procedure.
    :param driver:
    :return:
    """
    debug_log()
    url = driver.current_url
    u = urlparse(url).path
    if 'login' in u:
        log_in_and_catch(driver)


def read_from_file():
    with open(FA_FILE, 'r') as f:
        data = f.read()
    return data


def log_in_and_catch(driver):
    """
    Go through the log in procedure, catch and save the cookies

    :param driver:
    :return:
    """

    debug_log()
    try:
        seller_login_title = driver.find_element(
            By.XPATH,
            '//div[@data-tn="header-title" and text()="Seller Account Login"]'
            )
    except NoSuchElementException:
        seller_login_title = None

    if seller_login_title:
        email_field = driver.find_element("id", "input-:r0:")
        email_field.clear()
        email_field.send_keys(os.getenv("ADMIN_EMAIL"))
        time.sleep(2)
        password_field = driver.find_element("id", "input-:r1:")
        password_field.clear()
        password_field.send_keys(os.getenv("ADMIN_PASSWORD"))
        time.sleep(2)
        submit_button = driver.find_element(
            By.XPATH, '//button[@data-tn="login-submit"]'
            )
        submit_button.click()
        time.sleep(2)
        try:
            auth_field = driver.find_element("id", "input-:r2:")
        except NoSuchElementException:
            auth_field = None
        if auth_field:
            time.sleep(30)
            while True:
                try:
                    code_auth = read_from_file()
                    break
                except Exception as e:
                    exc_log(e)
                    time.sleep(10)

            auth_field.clear()
            auth_field.send_keys(str(code_auth))

            auth_button = driver.find_element(
                By.XPATH, '//button[@data-tn="login-submit"]'
            )
            auth_button.click()
        time.sleep(2)
        cookies = driver.get_cookies()
        with open("cookies.pkl", "wb") as file:
            pickle.dump(cookies, file)
