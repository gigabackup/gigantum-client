import time
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType, CompareUtilityType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ProjectActivityComponent(BaseComponent):
    """ Represents one of the components of project activity page.

       Holds a set of all locators within the activity tab on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ProjectActivityComponent, self).__init__(driver, component_data)
        self.activity_feed_main_div_element = "//div[@class='Activity__date-section Activity__date-section--0']"

    def click_activity_tab(self) -> bool:
        """ Performs click event on activity tab.

        Returns: returns the result of click action

        """
        element = "//li[@id='activity']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            activity_tab = self.get_locator(LocatorType.XPath, element)
            activity_tab.click()
            return True
        return False

    def verify_activity_feed(self, activity_feed_text: str) -> bool:
        """ Verify activity feed is present in the activity tab window

        Args:
            activity_feed_text: Activity feed text to be verify

        Returns: returns the result of verification

        """
        activity_feed_main_div = self.__get_activity_feed_main_div()
        if activity_feed_main_div is not None:
            activity_container = activity_feed_main_div.find_element_by_xpath\
                (".//div[@class='Activity__card-container Activity__card-container--last']")
            if activity_container is not None:
                activity_feed_text_element = f".//h6[contains(text(), '{activity_feed_text}')]"
                activity_feed_text = activity_container.wait_until\
                    (CompareUtilityType.CheckElement, 10, activity_feed_text_element)
                if activity_feed_text:
                    return True
        return False

    def __get_activity_feed_main_div(self) -> WebElement:
        """ Get activity feed man div web element

        Returns: returns activity feed main div web element

        """
        if self.check_element_presence(LocatorType.XPath, self.activity_feed_main_div_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            activity_feed_main_div = self.get_locator(LocatorType.XPath, self.activity_feed_main_div_element)
            if activity_feed_main_div is not None:
                return activity_feed_main_div

    def move_to_rollback_button_and_click(self, activity_feed_text: str) -> bool:
        """ Moves mouse focus to rollback button and performs click action

         Args:
            activity_feed_text: Activity feed text

        Returns: returns the result of click action

        """
        activity_feed_main_div = self.__get_activity_feed_main_div()
        if activity_feed_main_div is not None:
            activity_containers = activity_feed_main_div.find_elements_by_xpath\
                (".//div[@class='CardWrapper CardWrapper--rollback']")
            for activity_container in activity_containers:
                activity_feed_text_element = ".//h6[@class='ActivityCard__commit-message']"
                activity_feed = activity_container.find_element_by_xpath(activity_feed_text_element)
                if activity_feed_text in activity_feed.get_text().strip():
                    activity_rollback_element = ".//button[@class='Rollback__button']"
                    activity_rollback_button = activity_container.find_element_by_xpath(activity_rollback_element)
                    if activity_rollback_button is not None:
                        ActionChains(self.driver).move_to_element(activity_rollback_button).perform()
                        # Time sleep to make sure the activity rollback button is loaded
                        time.sleep(1)
                        activity_rollback_button.click()
                        return True
        return False

    def click_create_rollback_branch_button(self) -> bool:
        """ Performs click action on create rollback branch button.

        Returns: returns the result of click action

        """
        create_rollback_branch_button_element = "//button[@class='Btn ButtonLoader Btn--last']"
        if self.check_element_presence(LocatorType.XPath, create_rollback_branch_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            create_rollback_branch_button = self.get_locator(LocatorType.XPath, create_rollback_branch_button_element)
            create_rollback_branch_button.click()
            return True
        return False

    def verify_create_rollback_branch_window_opened(self) -> bool:
        """ Verify create rollback branch window is opened.

        Returns: returns the result of verification

        """
        create_rollback_branch_window_element = "//div[@class='Modal__content Modal__content--large rollback']"
        if self.check_element_presence(LocatorType.XPath, create_rollback_branch_window_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_create_rollback_branch_window_closed(self) -> bool:
        """ Verify create rollback branch window is closed or not.

        Returns: returns the result of verification

        """
        create_rollback_branch_window_element = "//div[@class='Modal__content Modal__content--large rollback']"
        if self.check_element_absence(LocatorType.XPath, create_rollback_branch_window_element,
                                      GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False
