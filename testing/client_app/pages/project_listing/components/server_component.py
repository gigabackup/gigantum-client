from client_app.constant_enums.constants_enums import GigantumConstants
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ServerComponent(BaseComponent):
    """ Represents one of the components of project listing page.

       Holds a set of all locators within the server window on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ServerComponent, self).__init__(driver, component_data)

    def click_server_tab(self) -> bool:
        """ Performs click action on server tab

        Returns: returns the result of click action

        """
        server_details = ProjectHelperUtility().get_server_details()
        server_tab = self.get_locator(LocatorType.XPath, f"//button[contains(text(),'"
                                                               f"{server_details['server_name']}')]")
        if server_tab is not None:
            server_tab.click()
            return True
        return False

    def verify_title_in_server(self, title) -> bool:
        """ Verify whether the title is present in the server page or not

        Args:
            title: Title of the project or dataset

        Returns: returns the result of title verification

        """
        element = "//div[@data-selenium-id='RemotePanel']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            title_list_div = self.driver.find_elements_by_xpath(element)
            if title_list_div is not None:
                for title_div in title_list_div:
                    title_name = title_div.find_element_by_xpath\
                        (".//div[@class='RemotePanel__row RemotePanel__row--title']/h5/div[1]")
                    if title == title_name.get_text().strip():
                        return True
        return False

    def click_import_button(self, title) -> bool:
        """ Performs click action on import button

        Args:
            title: Title of the current project or dataset

        Returns: returns the result of click action

        """
        element = "//div[@data-selenium-id='RemotePanel']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            title_list_div = self.driver.find_elements_by_xpath(element)
            if title_list_div is not None:
                for title_div in title_list_div:
                    title_text = title_div.find_element_by_xpath \
                        (".//div[@class='RemotePanel__row RemotePanel__row--title']/h5/div[1]")
                    if title == title_text.get_text().strip():
                        import_button = title_div.find_element_by_xpath(".//button[contains(text(),'Import')]")
                        if import_button is not None:
                            import_button.execute_script("arguments[0].click();")
                            return True
        return False

    def click_delete_button(self, title) -> bool:
        """ Performs click action on delete button

        Args:
            title: Title of the current dataset

        Returns: returns the result of click action

        """
        element = "//div[@data-selenium-id='RemotePanel']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            title_list_div = self.driver.find_elements_by_xpath(element)
            if title_list_div is not None:
                for title_div in title_list_div:
                    title_text = title_div.find_element_by_xpath\
                        (".//div[@class='RemotePanel__row RemotePanel__row--title']/h5/div[1]")
                    if title == title_text.get_text().strip():
                        delete_button = title_div.find_element_by_xpath(".//button[contains(text(),'Delete')]")
                        if delete_button is not None:
                            delete_button.execute_script("arguments[0].click();")
                            return True
        return False

    def get_title(self) -> str:
        """ Fetch title from the delete window

        Returns: returns title

        """
        element = "//div[@class='Modal__sub-container']/div[1]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            div_text = self.get_locator(LocatorType.XPath, element)
            title = div_text.find_element_by_xpath(".//b")
            return title.get_text().strip()

    def input_title(self, title) -> bool:
        """Input title for deletion

        Args:
            title: Title of the current project or dataset

        Returns:returns the result of input action

        """
        delete_input = self.get_locator(LocatorType.XPath, "//input[@id='deleteInput']")
        if delete_input is not None:
            delete_input.send_keys(title)
            return True
        return False

    def click_delete_button_on_window(self) -> bool:
        """Performs click action on delete button

        Returns: returns the result of click action

        """
        element = "//button[@data-selenium-id='ButtonLoader']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            btn_delete_project = self.get_locator(LocatorType.XPath, element)
            if btn_delete_project is not None and btn_delete_project.element_to_be_clickable():
                btn_delete_project.execute_script("arguments[0].click();")
                return True
        return False

    def verify_delete_modal_closed(self, wait_time: int) -> bool:
        """ Verify delete modal close after project / dataset deletion

        Args:
            wait_time: Time period for which the wait should continue

        Returns: returns the result of modal verification

        """
        element = "//div[@class='Icon Icon--delete']"
        return self.check_element_absence(LocatorType.XPath, element, wait_time)
