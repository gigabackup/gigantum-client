from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class DatasetListingComponent(BaseComponent):
    """ Represents one of the components of dataset listing page.

       Holds a set of all locators within the dataset listing components on the dataset listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(DatasetListingComponent, self).__init__(driver, component_data)

    def get_dataset_page_title(self) -> str:
        """Returns the title of dataset listing page."""
        txt_project_title = self.get_locator(LocatorType.XPath, "//h1[contains(text(),'Datasets')]")
        return txt_project_title.get_text()

    def check_add_dataset_title_presence(self) -> bool:
        """ Check for the presence of Add dataset title

        Returns: returns the result of title checking

        """
        element = "//h2[contains(text(), 'Add Dataset')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_create_new_dataset_button(self) -> bool:
        """Click action on create new dataset"""
        element = "//button[contains(text(), 'Create New')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            create_button = self.get_locator(LocatorType.XPath, element)
            if create_button is not None and create_button.element_to_be_clickable():
                create_button.execute_script("arguments[0].click();")
                return True
        return False

    def type_dataset_title(self, title: str) -> bool:
        """Input action for dataset title"""
        element = "//input[@id='CreateLabbookName']"
        dataset_title_input = self.get_locator(LocatorType.XPath, element)
        if dataset_title_input is not None:
            dataset_title_input.send_keys(title)
            return True
        return False

    def type_new_dataset_desc_textarea(self, desc: str) -> bool:
        """Input action for dataset description"""
        element = "//textarea[@id='CreateLabbookDescription']"
        dataset_desc_input = self.get_locator(LocatorType.XPath, element)
        if dataset_desc_input is not None:
            dataset_desc_input.send_keys(desc)
            return True
        return False

    def click_create_dataset_button(self) -> bool:
        """Click action for create new dataset button"""
        element = "//button[@data-selenium-id='ButtonLoader']"
        create_dataset_button = self.get_locator(LocatorType.XPath, element)
        if create_dataset_button is not None:
            create_dataset_button.click()
            return True
        return False

    def select_dataset(self, dataset_title) -> bool:
        """ Click on the dataset in dataset listing page

        Args:
            dataset_title: Title of the dataset

        Returns: returns the result of click action

        """
        element = "//a[@class='Card Card--225 Card--text column-4-span-3 flex flex--column justify--space-between']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            datasets_list = self.driver.find_elements_by_xpath(element)
            if datasets_list is not None:
                for dataset in datasets_list:
                    dataset_name = dataset.find_element_by_xpath(".//div[@class='LocalPanel__row--text']/div/h5/div")
                    if dataset_title == dataset_name.get_text().strip():
                        dataset.click()
                        return True
        return False

    def verify_dataset_in_dataset_listing(self, dataset_title) -> bool:
        """ Verify whether the dataset is present in the dataset listing page or not

        Args:
            dataset_title: Title of the dataset

        Returns: returns the result of dataset verification

        """
        element = "//a[@class='Card Card--225 Card--text column-4-span-3 flex flex--column justify--space-between']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            datasets_list = self.driver.find_elements_by_xpath(element)
            if datasets_list is not None:
                for dataset in datasets_list:
                    dataset_name = dataset.find_element_by_xpath(".//div[@class='LocalPanel__row--text']/div/h5/div")
                    if dataset_title == dataset_name.get_text().strip():
                        return False
        return True

    def click_import_existing_dataset_button(self) -> bool:
        """Click action on import existing button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Import Existing')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            import_existing_button = self.get_locator(LocatorType.XPath, element)
            if import_existing_button is not None and import_existing_button.element_to_be_clickable():
                import_existing_button.execute_script("arguments[0].click();")
                return True
        return False

    def type_dataset_import_url(self, import_url: str) -> bool:
        """Input action for dataset import url

        Args:
            import_url: URL of the dataset to be import

        Returns: returns the result of input action

        """
        element = "//input[@class='Import__input']"
        dataset_title_input = self.get_locator(LocatorType.XPath, element)
        if dataset_title_input is not None:
            dataset_title_input.send_keys(import_url)
            return True
        return False

    def click_import_dataset_button(self) -> bool:
        """ Click action for import dataset button

        Returns: returns the result of click action

        """
        element = "//div[@class='Import__buttonContainer']/button[@class='Btn--last']"
        import_dataset_button = self.get_locator(LocatorType.XPath, element)
        if import_dataset_button is not None and import_dataset_button.element_to_be_clickable():
            import_dataset_button.execute_script("arguments[0].click();")
            return True
        return False

    def verify_dataset_import_error(self) -> bool:
        """ Verify whether the import error pop up is shown or not

        Returns: returns the result of import error verification

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'ERROR: Could not import remote Dataset')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_dataset_import_success(self) -> bool:
        """ Verify whether the import success pop up is shown or not

        Returns: returns the result of import success verification

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'Successfully imported remote Dataset')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_dataset_permission_error(self) -> bool:
        """ Verify whether the dataset permission error pop up is shown or not

        Returns: returns the result of dataset permission error verification

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed' and contains(text(), " \
                  "'You do not have adequate permissions to modify this dataset')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

