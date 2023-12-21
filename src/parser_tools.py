import os
import pickle
import time
import pathlib
import dotenv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from .logger import exc_log, debug_log
from .stats_data import check_chat_id, show_processed_chats, add_processed
from .cookies_cather import checking_logout


dotenv.load_dotenv()


CONVERSATIONS_URL = os.getenv("CONV_URL")
OWNER_NAME = os.getenv("OWNER_NAME")
ANSWER_MSG = (
        "We appreciate that you are interested in our products.\n"
        "We have forwarded your request to the manager who will contac t"
        "you shortly.\n"
        f"Best regards,\n{OWNER_NAME}"
    )

# setup chromedriver
current_path = pathlib.Path(__file__).parent
driver_path = current_path / 'chromedriver-win64' / 'chromedriver.exe'
webdriver_service = Service(service_path=driver_path)
driver = webdriver.Chrome(service=webdriver_service)

# run google chrome
driver.maximize_window()
time.sleep(1)

# Checking if we need to log in
checking_logout(driver)

# go to conversations
try:
    driver.get(CONVERSATIONS_URL)
except Exception as ex:
    exc_log(ex)
driver.refresh()
time.sleep(2)


def set_cookies():
    """
    download cookies
    """
    debug_log()
    try:
        with open("cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        debug_log("Cookies file not found")


def upd_cookies():
    """
    catch and save cookie
    """
    debug_log()
    cookies = driver.get_cookies()
    with open("cookies.pkl", "wb") as file:
        pickle.dump(cookies, file)


def is_modal_present():
    """
    check if modal present

    :return:
    """
    debug_log()
    try:
        modal_xpath = (
            "//div[@data-dibs-modal='true' and starts-with(@id, 'Modal:rh:')]"
            " | "
            "//div[@data-dibs-modal='true' and starts-with(@id, 'Modal:rg:')]"
            )
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, modal_xpath)
            )
        )
        return True
    except Exception as e:
        debug_log(e)
        return False


def is_modal_private_offer():
    """
    check if modal present

    :return:
    """
    debug_log()
    try:
        WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.XPATH, "//div[@data-dibs-modal='true']")
            )
        )
        return True
    except Exception as e:
        debug_log(e)
        return False


def parsing_conversation():
    """
    parsing conversation, find and return unread chat's

    :return: dict with unread chats id
    """

    debug_log()
    unread_msg = {}

    def get_convers():
        debug_log()
        driver.get(CONVERSATIONS_URL)
        WebDriverWait(driver, 30).until(
            ec.presence_of_element_located(
                (By.XPATH, '//*[@data-tn="conversation-list"]')
                )
        )

    while True:
        try:
            get_convers()
            break
        except Exception as e:
            exc_log(e)
            driver.refresh()
            time.sleep(300)

    time.sleep(2)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    conversations = soup.find_all("a", class_="gtm-conversation-summary")

    for item in conversations:
        # checking for "unread" flag
        if item.find("div", {"data-tn": "mc-conv-summary-indicator-unread"}):
            msg_id = item.get("data-conversation-id")
            buyer_name_span = item.find(
                "span", {"data-tn": "mc-conv-summary-buyer-name"}
                )
            buyer_name = buyer_name_span.get_text(strip=True)

            # checking if the chat has been processed before
            if check_chat_id(msg_id):
                unread_msg.update({msg_id: buyer_name})
    return unread_msg


def write_answer():
    """
    bypassing all kinds of obstacles (modal windows, additional buttons that
    are not always present) and responding to the user
    :return:
    """
    debug_log()
    time.sleep(3)
    checking = is_modal_present()
    if checking:
        close_button = driver.find_element(
            By.XPATH, "//button[@data-tn='modal-close-button']"
        )
        close_button.click()
    time.sleep(2)

    def reply_button_clk():
        """
        find and click on reply button
        """
        debug_log()
        element = WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located(
                (By.XPATH, "//div[@data-tn='action-sheet-toggle-children']")
            )
        )
        # scroll down to element
        driver.execute_script(
            "arguments[0].scrollIntoView();",
            element
        )
        time.sleep(3)
        reply_button = driver.find_element(
            By.XPATH,
            "//div[@data-tn='action-sheet-toggle-children']")
        reply_button.click()
        time.sleep(5)

    while True:
        try:
            reply_button_clk()
            break
        except Exception as e:
            exc_log(e)
            driver.refresh()
            time.sleep(120)

    # find textarea and write answer text
    rep_with_msg = driver.find_element(
        By.XPATH,
        "//div[@data-tn='action-sheet-message-cta']"
        )
    rep_with_msg.click()
    time.sleep(3)

    text_field = driver.find_element(
        By.XPATH,
        "//textarea[@data-tn='compose-message-textarea']"
        )
    text_field.clear()

    text_field.send_keys(ANSWER_MSG)
    time.sleep(5)
    # find button SEND and click
    msg_submit = driver.find_element(
        By.XPATH,
        "//button[@data-tn='compose-message-submit']"
    )
    time.sleep(3)
    msg_submit.click()

    private_offer = is_modal_private_offer()
    if private_offer:
        button = driver.find_element(
            By.XPATH,
            "//button[text()='Send Message Without a Private Offer']"
            )
        # Click the button
        driver.execute_script("arguments[0].click();", button)


def mark_as_unread(chat_id):
    """
    Return to conversations and mark current chat as unread

    :param chat_id:
    :return:
    """
    debug_log(chat_id)
    driver.get(CONVERSATIONS_URL)
    time.sleep(1)
    while True:
        try:
            WebDriverWait(driver, 30).until(
                ec.presence_of_element_located(
                    (By.ID, f"conversationSelect{chat_id}")))
            # choose chat in chat_list
            checkbox = driver.find_element(
                By.ID, f"conversationSelect{chat_id}"
                )
            driver.execute_script("arguments[0].click();", checkbox)
            # make chat unread again
            button = driver.find_element(
                By.XPATH, "//a[@data-tn='mc-dealer-bulk-actions-mark-unread']"
                )
            button.click()
            time.sleep(5)
            break
        except Exception as e:
            exc_log(e)
            driver.refresh()
            time.sleep(120)


def processing_chat(chat_id, buyer_name):
    """
    Parse correspondence, collect and analyze data. Add the chat to the list
    of processed ones and mark them as unread.
    If the received data meets the criteria -no response from the seller in the
    chat - respond to the buyer

    :param chat_id:
    :param buyer_name:
    :return:
    """
    debug_log(chat_id)

    def go_into_chat():
        debug_log(chat_id)
        time.sleep(5)
        chat_url = f"{CONVERSATIONS_URL}{chat_id}"
        driver.get(chat_url)

    while True:
        try:
            go_into_chat()
            break
        except Exception as e:
            exc_log(e)
            driver.refresh()
            time.sleep(120)

    # wait until all the necessary elements are loaded
    WebDriverWait(driver, 60).until(
        ec.presence_of_element_located(
            (By.XPATH, '//*[@data-tn="message-wrapper"]')
        )
    )

    # capturing a block with chat
    element = driver.find_element(
        By.XPATH, '//*[@id="js-root"]/div/div/div/div/div[2]/div[2]'
    )
    element_html = element.get_attribute('outerHTML')
    soup = BeautifulSoup(element_html, 'lxml')
    valid_data = ['message-wrapper', 'message-date']
    elements = soup.find_all(
        lambda tag: tag.name == 'div' and tag.get('data-tn') in valid_data
    )

    chat_data_dict = {}
    current_date = None  # to keep track of the current date while iterating
    for item in elements:
        if item.get('data-tn') == 'message-date':
            date = item.find('span').get_text(strip=True).split(',')[1].strip()
            current_date = date
            chat_data_dict[current_date] = []
        elif item.get('data-tn') == 'message-wrapper':
            user_span = item.find('span', attrs={'data-tn': 'message-title'})
            for child in user_span.find_all():
                child.decompose()
            time_span = item.find('span', attrs={'data-tn': 'message-time'})
            for child in time_span.find_all():
                child.decompose()

            user_name = user_span.get_text(strip=True)
            msg_time = time_span.get_text(strip=True)
            if current_date:
                chat_data_dict[current_date].append({user_name: msg_time})

    # Convert the chat_data_dict to a list of single-key dictionaries
    chat_data = [{date: user_items} for date, user_items
                 in chat_data_dict.items()]

    last_write = {}
    day_count = 0
    guest_msg = 0
    owner_msg = 0
    for dicts in chat_data[::-1]:
        for date, inner_list in dicts.items():
            if len(inner_list) == 0:
                continue
            day_count += 1
            inner_list = inner_list[::-1]
            if len(last_write) == 0:
                name = list(inner_list[0].keys())[0]
                last_write = {'name': name,
                              'date': date,
                              'time': inner_list[0].get(name)}
            for item in inner_list:
                for user in item.keys():
                    if user == OWNER_NAME:
                        owner_msg += 1
                    else:
                        guest_msg += 1

    if owner_msg == 0 and guest_msg > 0:
        write_answer()

    add_processed(chat_id, buyer_name, False)
    mark_as_unread(chat_id)


def main_engine():
    """
    The main script that launches all the necessary functions in a certain
    sequence
    :return:
    """
    set_cookies()
    driver.refresh()
    checking_logout(driver)

    try:
        driver.get(CONVERSATIONS_URL)
    except Exception as e:
        exc_log(e)

    unread_messages = parsing_conversation()
    driver.refresh()
    checking_logout(driver)
    debug_log(f"unread chats: {unread_messages}")
    # show current statistics
    show_processed_chats()
    # checking if the chat has been processed before
    for chat_id, buyer_name in unread_messages.items():
        if check_chat_id(chat_id):
            processing_chat(chat_id, buyer_name)
    driver.get(CONVERSATIONS_URL)
    upd_cookies()
