from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class DatasetDeleteComponent(BaseComponent):
    """ Represents one of the components of Dataset listing page.

       Holds a set of all locators within the Delete dataset window on the dataset listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(DatasetDeleteComponent, self).__init__(driver, component_data)

    def get_dataset_title(self) -> str:
        """ Fetch dataset title from the delete dataset window

        Returns: returns dataset title

        """
        element = "//div[@class='Modal__sub-container']/div[1]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            div_text = self.get_locator(LocatorType.XPath, element)
            project_title = div_text.find_element_by_xpath(".//b")
            return project_title.get_text().strip()

    def input_dataset_title(self, dataset_title) -> bool:
        """Input dataset title for deletion

        Args:
            dataset_title: Title of the current dataset

        Returns:

        """
        delete_input = self.get_locator(LocatorType.XPath, "//input[@id='deleteInput']")
        if delete_input is not None:
            delete_input.send_keys(dataset_title)
            return True
        return False

    def click_delete_button(self) -> bool:
        """Performs click action on delete button on delete dataset window

        Returns: returns the result of click action

        """
        element = "//button[@data-selenium-id='ButtonLoader']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            btn_delete_project = self.get_locator(LocatorType.XPath, element)
            if btn_delete_project is not None and btn_delete_project.element_to_be_clickable():
                btn_delete_project.execute_script("arguments[0].click();")
                return True
        return False
