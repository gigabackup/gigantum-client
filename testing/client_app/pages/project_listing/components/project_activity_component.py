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
        activity_feed_main_div_element = "//div[@class='Activity__date-section Activity__date-section--0']"
        if self.check_element_presence(LocatorType.XPath, activity_feed_main_div_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            activity_feed_main_div = self.get_locator(LocatorType.XPath, activity_feed_main_div_element)
            if activity_feed_main_div is not None:
                activity_container = activity_feed_main_div.find_element_by_xpath\
                    (".//div[@class='Activity__card-container Activity__card-container--last']")
                if activity_container is not None:
                    activity_feed_text_element = f".//h6[contains(text(), '{activity_feed_text}')]"
                    activity_feed_text = activity_container.wait_until\
                        (CompareUtilityType.CheckElement, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value,
                         activity_feed_text_element)
                    if activity_feed_text:
                        return True
        return False
