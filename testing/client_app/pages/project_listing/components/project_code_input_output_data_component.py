from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ProjectCodeInputOutputDataComponent(BaseComponent):
    """ Represents one of the components of project listing page.

       Holds a set of all locators within the code, input and output tab on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ProjectCodeInputOutputDataComponent, self).__init__(driver, component_data)

    def drag_and_drop_text_file_in_code_drop_zone(self, file_content: str) -> bool:
        """Drag and drop the text file into Code data drop zone

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='Dropbox "
                                                       "Dropbox--fileBrowser flex flex--column align-items--center']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def drag_and_drop_text_file_in_input_drop_zone(self, file_content: str) -> bool:
        """Drag and drop the text file into Input data drop zone

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@data-selenium-id='FileBrowser']/div[4]/div[3]")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def drag_and_drop_text_file_in_output_drop_zone(self, file_content: str) -> bool:
        """Drag and drop the text file into Output data drop zone

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='Dropbox "
                                                       "Dropbox--fileBrowser flex flex--column align-items--center']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def drag_and_drop_text_file_in_code_file_browser(self, file_content: str) -> bool:
        """Drag and drop the text file in to code data file browser

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='FileBrowser']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def drag_and_drop_text_file_in_input_file_browser(self, file_content: str) -> bool:
        """Drag and drop the text file in to input data file browser

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='FileBrowser']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def drag_and_drop_text_file_in_output_file_browser(self, file_content: str) -> bool:
        """Drag and drop the text file in to output data file browser

        Args:
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='FileBrowser']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_content=file_content)
            return True
        return False

    def click_link_dataset_button(self) -> bool:
        """ Performs click action on link dataset button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Link Dataset')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            link_dataset_button = self.get_locator(LocatorType.XPath, element)
            link_dataset_button.execute_script("arguments[0].click();")
            return True
        return False

    def select_dataset(self, dataset_title: str):
        """ Select dataset from the link dataset window

        Args:
            dataset_title: Title of the dataset to be linked

        Returns: returns the result of dataset selection

        """
        element = "//div[@class='LinkModal__wrapper']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            dataset_div_list = self.driver.find_elements_by_xpath(element)
            for dataset_div in dataset_div_list:
                dataset_title_element = dataset_div.find_element_by_xpath(".//h6[@class='LinkCard__header']/b")
                if dataset_title == dataset_title_element.get_text().strip():
                    dataset_div.execute_script("arguments[0].click();")
                    return True
        return False

    def click_link_dataset_button_on_link_dataset_window(self):
        """ Performs click action on link dataset button on link dataset window

        Returns: returns the result of click action

        """
        element = "//button[@class='Btn ButtonLoader Btn Btn--last']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            dataset_link_button = self.get_locator(LocatorType.XPath, element)
            dataset_link_button.execute_script("arguments[0].click();")
            return True
        return False

    def check_link_dataset_window_closed(self) -> bool:
        """ Check for the absence of link dataset window

        Returns: returns True if the element is not present

        """
        element = "//h4[@class='LinkModal__header-text' and text()='Link Dataset']"
        if self.check_element_absence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_input_download_all_button(self):
        """ Performs click action on download all button on input data tab

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Download All')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            download_all_button = self.get_locator(LocatorType.XPath, element)
            download_all_button.execute_script("arguments[0].click();")
            return True
        return False

    def check_download_complete_pop_up_presence(self):
        """ Check for the presence of download complete pop up

        Returns: returns the result of pop up presence check

        """
        element = "//p[contains(text(), 'Download complete!')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_files_are_downloaded(self):
        """ Verify files are downloaded or not

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Downloaded')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_dataset_is_present(self, dataset_name: str) -> bool:
        """ Verify dataset is present on input data tab

        Args:
            dataset_name: Name of the dataset

        Returns: returns the result of verification

        """
        element = f"//div[@class='DatasetCard Card']/div/div[2]/div[2]/a[contains(text(), {dataset_name})]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_dataset_name(self, dataset_name: str) -> bool:
        """ Performs click action on dataset name on input data tab

        Args:
            dataset_name: Name of the dataset

        Returns: returns the result of click action

        """
        element = f"//div[@class='DatasetCard Card']/div/div[2]/div[2]/a[contains(text(), {dataset_name})]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            dataset_title_element = self.get_locator(LocatorType.XPath, element)
            dataset_title_element.click()
            return True
        return False

    def click_file_delete(self, file_name: str) -> bool:
        """ Performs click action on file delete button

        Args:
            file_name: Name of the file to be delete

        Returns: returns the result of click action

        """
        element = "//div[@class='File']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            file_div_list = self.driver.find_elements_by_xpath(element)
            for file_div in file_div_list:
                file_title_div = file_div.find_element_by_xpath(".//div[@class='File__text']/div")
                if file_name == file_title_div.get_text().strip():
                    file_delete_button = file_div.find_element_by_xpath(".//button[@class='ActionsMenu__item Btn "
                                                                        "Btn--fileBrowser Btn__delete-secondary "
                                                                        "Btn--round']")
                    file_delete_button.click()
                    tick_button = file_div.find_element_by_xpath(".//button[@class='File__btn--round File__btn--add']")
                    if tick_button is not None:
                        tick_button.click()
                        return True
        return False

    def verify_file_is_present(self, file_name: str) -> bool:
        """ Verify file is present in the code tab window

        Args:
            file_name: Name of the file to be verify

        Returns: returns the result of verification

        """
        element = f"//div[@class='File']/div/div[1]/div[2]/div[contains(text(), '{file_name}')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False
