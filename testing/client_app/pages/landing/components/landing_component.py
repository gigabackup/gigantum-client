from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from collections import namedtuple


class LandingComponent(BaseComponent):
    """Represents one of the components of landing page.

    Holds a set of all locators within the user login frame on the landing page of
    gigantum client as an entity. Handles events and test functions of locators
    in this entity.
    """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(LandingComponent, self).__init__(driver, component_data)

    def click_server(self, server_name) -> bool:
        """Performs navigation to login page.

        Click event on the sign-in button is performed,
        and login page is displayed.

        """
        element = f"//button[contains(text(), '{server_name}')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            server_button = self.get_locator(LocatorType.XPath, element)
            server_button.click()
            return True
        return False
