# Builtin imports
import subprocess
import logging
import shutil
import time
import uuid
import glob
import uuid
import sys
import os
import requests

from functools import wraps

# Library imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def TestTags(*taglist):
    """ This is used to append tags to tests, such that the driver
     filters and only execute tests that match. """
    print(taglist)
    def wrapper(f, *ar, **kwar):
        @wraps(f)
        def wrapped(driver, *fargs, **fkwargs):
            return f(driver, *ar, *kwar)
        return wrapped
    return wrapper


def load_chrome_driver():
    """ Return Chrome webdriver """
    options = Options()
    options.add_argument("--incognito")
    return webdriver.Chrome(options=options)


def load_chrome_driver_headless():
    """ Return headless Chrome webdriver """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--incognito")
    return webdriver.Chrome(options=options)


def load_firefox_driver():
    """ Return Firefox webdriver """
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)

    return webdriver.Firefox(firefox_profile=firefox_profile)


def unique_project_name(prefix: str = "selenium-project"):
    """ Return a universally-unique project name """
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


def unique_dataset_name(prefix: str = "selenium-dataset"):
    """ Return a universally-unique dataset name """
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


def unique_project_description():
    """ Return a universally-unique project description """
    return ''.join([str(uuid.uuid4())[:6] for num in range(30)])


def load_credentials(path: str = 'credentials.txt', user_index: int = 0):
    """ Return tuple of username and password """
    assert os.path.exists(path), f"Specificy login credentials in {path}"
    with open(path) as cfile:
        lines = cfile.readlines()
        assert len(lines) >= 2, f"Must have line for username and password in {path}"
    # return username (first line) and password (second line)
    return lines[2 * user_index].strip(), lines[(2 * user_index) + 1].strip()


def is_container_stopped(driver):
    """ Check if the container is stopped """
    return driver.find_element_by_css_selector(".flex>.Stopped").is_displayed()


def stop_container(driver):
    """ Stop container after test is finished """
    return driver.find_element_by_css_selector(".flex>.Running").click()


def project_title_correct(project_title: str, expected_project_title: str) -> bool:
    """Helper method to match a project title that may or may not be shortened with a `...` in the middle

    Args:
        project_title:
        expected_project_title:

    Returns:
        True if the title matches, false if it does not
    """
    if "..." in project_title:
        _, _, hashstr = expected_project_title.split('-')
        if "selenium-" in project_title and f"-{hashstr}" in project_title:
            return True
        else:
            return False
    else:
        return project_title == expected_project_title


def current_server_id() -> str:
    """Helper to get the current server id"""
    rsp = requests.get("http://localhost:10000/api/servers")
    if rsp.status_code != 200:
        raise ValueError("Failed to fetch current server id")

    return rsp.json()['current_server']

