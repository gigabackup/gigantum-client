from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ProjectListingComponent(BaseComponent):
    """ Represents one of the components of project listing page.

       Holds a set of all locators within the title layout on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ProjectListingComponent, self).__init__(driver, component_data)

    def get_project_title(self) -> str:
        """Returns the title of project listing page."""
        element = "//h1[contains(text(),'Projects')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            txt_project_title = self.get_locator(LocatorType.XPath, element)
            if txt_project_title is not None:
                return txt_project_title.get_text()

    def profile_menu_click(self) -> bool:
        """Performs click event of profile menu item."""
        btn_profile_menu = self.get_locator(LocatorType.XPath, "//h6[@id='username']")
        if btn_profile_menu is not None:
            btn_profile_menu.click()
            return True
        return False

    def log_out(self) -> bool:
        """Performs click event of logout menu item."""
        btn_logout = self.get_locator(LocatorType.XPath, "//button[@id='logout']")
        if btn_logout is not None:
            btn_logout.click()
            return True
        return False

    def verify_project_in_project_listing(self, project_title) -> bool:
        """ Verify whether the project is present in the project listing page or not

        Args:
            project_title: Title of the current project

        Returns: returns the result of project verification

        """
        element = "//a[@class='Card Card--225 Card--text column-4-span-3 flex flex--column justify--space-between']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            projects_list = self.driver.find_elements_by_xpath(element)
            if projects_list is not None:
                for project in projects_list:
                    project_name = project.find_element_by_xpath(".//div[@class='LocalPanel__row--text']/div/h5/div")
                    if project_title == project_name.get_text().strip():
                        return False
        return True

    def click_project(self, project_title) -> bool:
        """ Click on the project in project listing

        Args:
            project_title: Title of the current project

        Returns: returns the result of click action

        """
        element = "//a[@class='Card Card--225 Card--text column-4-span-3 flex flex--column justify--space-between']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            projects_list = self.driver.find_elements_by_xpath(element)
            if projects_list is not None:
                for project in projects_list:
                    project_name = project.find_element_by_xpath(".//div[@class='LocalPanel__row--text']/div/h5/div")
                    if project_title == project_name.get_text().strip():
                        project.click()
                        return True
        return False

    def click_import_existing_project_button(self) -> bool:
        """Click action on import existing project button
        Returns: returns the result of click action
        """
        element = "//button[contains(text(), 'Import Existing')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            import_existing_project_button = self.get_locator(LocatorType.XPath, element)
            if import_existing_project_button is not None and import_existing_project_button.element_to_be_clickable():
                import_existing_project_button.click()
                return True
        return False

    def type_project_import_url(self, import_url: str) -> bool:
        """Input action for project import url
        Args:
            import_url: URL of the project to be import
        Returns: returns the result of input action
        """
        element = "//input[@class='Import__input']"
        project_title_input = self.get_locator(LocatorType.XPath, element)
        if project_title_input is not None:
            project_title_input.send_keys(import_url)
            return True
        return False

    def click_import_project_button(self) -> bool:
        """ Click action for import project button
        Returns: returns the result of click action
        """
        element = "//div[@class='Import__buttonContainer']/button[@class='Btn--last']"
        import_project_button = self.get_locator(LocatorType.XPath, element)
        if import_project_button is not None and import_project_button.element_to_be_clickable():
            import_project_button.execute_script("arguments[0].click();")
            return True
        return False

    def verify_project_import_error(self) -> bool:
        """ Verify whether the import error for project pop up is shown or not
        Returns: returns the result of import project error verification
        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'ERROR: Could not import remote Project')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_project_import_success(self) -> bool:
        """ Verify whether the import project success pop up is shown or not
        Returns: returns the result of import project success verification
        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'Successfully imported remote Project')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

