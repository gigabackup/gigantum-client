from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ProjectMenuComponent(BaseComponent):
    """ Represents one of the components of project listing page.

       Holds a set of all menu and button locators on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ProjectMenuComponent, self).__init__(driver, component_data)

    def get_title(self) -> str:
        """ Get the title from the listing page

        Returns: returns title

        """
        element = "//div[@class='TitleSection__namespace-title']"
        title = self.get_locator(LocatorType.XPath, element)
        if title is not None:
            title = title.get_text().split('/')[-1].strip()
            return title

    def click_code_data_tab(self) -> bool:
        """ Performs click event on code data tab.

        Returns: returns the result of click action

        """
        element = "//li[@id='code']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            code_data_tab = self.get_locator(LocatorType.XPath, element)
            code_data_tab.click()
            return True
        return False

    def click_input_data_tab(self) -> bool:
        """ Performs click event on input data tab.

        Returns: returns the result of click action

        """
        element = "//li[@id='inputData']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            input_data_tab = self.get_locator(LocatorType.XPath, element)
            input_data_tab.click()
            return True
        return False

    def click_output_data_tab(self) -> bool:
        """ Performs click event on output data tab.

        Returns: returns the result of click action

        """
        element = "//li[@id='outputData']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            output_data_tab = self.get_locator(LocatorType.XPath, element)
            output_data_tab.click()
            return True
        return False

    def click_publish_button(self) -> bool:
        """ Performs click action on publish button

        Returns: returns the result of click action

        """
        element = "//div[contains(text(), 'Publish')]"
        btn_publish = self.get_locator(LocatorType.XPath, element)
        if btn_publish is not None and btn_publish.element_to_be_clickable():
            btn_publish.click()
            return True
        return False

    def enable_private_mode(self) -> bool:
        """ Enable private mode in publish project by clicking radio button

        Returns: returns the result of radio button click

        """
        element = "//div[@class='VisibilityModal__private']/label"
        btn_publish_private = self.get_locator(LocatorType.XPath, element)
        if btn_publish_private is not None:
            btn_publish_private.click()
            return True
        return False

    def click_publish_window_button(self) -> bool:
        """ Performs click action on publish button on project publish window

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Publish')]"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            publish_button = self.get_locator(LocatorType.XPath, element)
            if publish_button is not None:
                publish_button.click()
                return True
        return False

    def check_private_lock_icon_presence(self) -> bool:
        """ Performs checking for lock icon presence

        Returns: returns the result of checking

        """
        element = "//div[@class='TitleSection__private Tooltip-data Tooltip-data--small']"
        if self.check_element_presence(LocatorType.XPath, element, 120):
            return True
        return False

    def click_sync_button(self) -> bool:
        """ Performs click action on sync button

        Returns: returns the result of click action

        """
        element_sync_needed = "//button[@class='Btn--branch Btn--action SyncBranchButtons__btn Tooltip-data']"
        element_up_to_date = "//button[@class='Btn--branch Btn--action SyncBranchButtons__btn " \
                             "SyncBranchButtons__btn--upToDate Tooltip-data']"
        if self.check_element_presence(LocatorType.XPath, element_sync_needed, 5):
            sync_button = self.get_locator(LocatorType.XPath, element_sync_needed)
            if sync_button is not None and sync_button.element_to_be_clickable():
                sync_button.click()
                return True
        elif self.check_element_presence(LocatorType.XPath, element_up_to_date, 5):
            sync_button = self.get_locator(LocatorType.XPath, element_up_to_date)
            if sync_button is not None and sync_button.element_to_be_clickable():
                sync_button.click()
                return True

        return False

    def click_project_menu_button(self) -> bool:
        """Performs click action on project menu button

        Returns: returns the result of click action

        """
        btn_project_menu = self.get_locator(LocatorType.XPath, "//button[@class='ActionsMenu__btn Btn--last']")
        if btn_project_menu is not None:
            btn_project_menu.click()
            return True
        return False

    def click_delete_project_menu(self) -> bool:
        """Performs click action on delete project menu

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Delete Project')]"
        menu_project_delete = self.get_locator(LocatorType.XPath, element)
        if menu_project_delete is not None:
            menu_project_delete.click()
            return True
        return False

    def click_collaborators_button(self) -> bool:
        """Performs click action on Collaborators button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Collaborators')]"
        btn_collaborators = self.get_locator(LocatorType.XPath, element)
        if btn_collaborators is not None:
            btn_collaborators.click()
            return True
        return False

    def check_upload_complete_pop_up_presence(self) -> bool:
        """ Check for the presence of upload complete pop up message

        Returns: returns True if the element is present

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'Upload complete!')]"
        if self.check_element_presence(LocatorType.XPath, element, 60):
            return True
        return False

    def check_upload_complete_pop_up_absence(self) -> bool:
        """ Check for the absence of upload complete pop up message

        Returns: returns True if the element is not present

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and " \
                  "text()='Upload complete!']"
        if self.check_element_absence(LocatorType.XPath, element, 40):
            return True
        return False

    def check_sync_complete_pop_up_presence(self) -> bool:
        """ Check for the presence of sync complete pop up message

        Returns: returns True if the element is present

        """
        element = "//p[contains(text(), 'Sync complete')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            return True
        return False

    def check_sync_complete_pop_up_absence(self) -> bool:
        """ Check for the absence of sync complete pop up message

        Returns: returns True if the element is not present

        """
        element = "//p[contains(text(), 'Sync complete')]"
        if self.check_element_absence(LocatorType.XPath, element, 30):
            return True
        return False

    def click_projects_menu(self) -> bool:
        """Performs click action on projects menu

        Returns: returns the result of click action

        """
        element = "//a[contains(text(), 'Projects')]"
        projects_menu = self.get_locator(LocatorType.XPath, element)
        if projects_menu is not None:
            projects_menu.click()
            return True
        return False

    def check_sync_button_is_enabled(self) -> bool:
        """ Check sync button is enabled or not

        Returns:returns the result of sync button enabled state

        """
        element = "//button[@data-tooltip='Cannot Sync while Dataset is in use']"
        if self.check_element_absence(LocatorType.XPath, element, 40):
            return True
        return False
