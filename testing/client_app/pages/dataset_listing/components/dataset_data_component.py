from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from selenium.webdriver.common.action_chains import ActionChains
import time
import pkg_resources


class DatasetDataComponent(BaseComponent):
    """ Represents one of the components of dataset listing page.

       Holds a set of all locators within the Data tab components on the dataset listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(DatasetDataComponent, self).__init__(driver, component_data)

    def drag_and_drop_text_file_in_data_drop_zone(self, file_name: str, file_content: str) -> bool:
        """Drag and drop the text file into Input data drop zone

        Args:
            file_name: Name of the file
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='Dropbox "
                                                       "Dropbox--fileBrowser flex flex--column align-items--center']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_name=file_name, file_content=file_content)
            return True
        return False

    def click_new_folder_button(self) -> bool:
        """ Performs click action on new folder button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'New Folder')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            new_folder_button = self.get_locator(LocatorType.XPath, element)
            if new_folder_button is not None and new_folder_button.is_enabled():
                new_folder_button.click()
                return True
        return False

    def type_new_folder_name(self, folder_name) -> bool:
        """ Type new folder name

        Args:
            folder_name: Name of the new folder

        Returns: returns the result of folder name input action

        """
        element = "//input[@placeholder='Enter Folder Name']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            folder_name_input = self.get_locator(LocatorType.XPath, element)
            folder_name_input.send_keys(folder_name)
            return True
        return False

    def check_file_uploading_progress_bar_presence(self) -> bool:
        """ Check for the presence of file uploading progress bar

        Returns: returns the result of progress bar checking

        """
        element = "//div[@class='FooterUploadBar__message' and text()='Please wait while contents are analyzed.']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            return True
        return False

    def check_file_uploading_progress_bar_absence(self) -> bool:
        """ Check for the presence of file uploading progress bar

        Returns: returns the result of progress bar checking

        """
        element = "//div[@class='FooterUploadBar__message']/div[@class='FooterUploadBar__progressBar " \
                  "FooterUploadBar__progressBar--animation']"
        if self.check_element_absence(LocatorType.XPath, element, 30):
            return True
        return False

    def click_add_button(self) -> bool:
        """ Performs click action on add button

        Returns: returns the result of click action

        """
        element = "//button[@class='File__btn--round File__btn--add']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            new_folder_add_button = self.get_locator(LocatorType.XPath, element)
            if new_folder_add_button is not None and new_folder_add_button.is_enabled():
                new_folder_add_button.click()
                return True
        return False

    def verify_download_all_files_button_is_enabled(self) -> bool:
        """ Verify all files need to be download

        Returns: returns the result of verification

        """
        element = "//button[contains(text(), 'Download All')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            download_all_file_button = self.get_locator(LocatorType.XPath, element)
            if download_all_file_button is not None and download_all_file_button.is_enabled():
                return True
        return False

    def click_file_download(self, file_name) -> bool:
        """ Performs click action on file download button

        Args:
            file_name: Name of the file to be download

        Returns: returns the result of click action

        """
        element = "//div[@class='File']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            file_div_list = self.driver.find_elements_by_xpath(element)
            for file_div in file_div_list:
                file_title_div = file_div.find_element_by_xpath(".//div[@id='Tooltip--file']")
                if file_name == file_title_div.get_text().strip():
                    file_download_button = file_div.find_element_by_xpath(".button[contains(text(), 'Download')]")
                    file_download_button.click()
                    return True
        return False

    def check_download_complete_pop_up_presence(self) -> bool:
        """ Check for the presence of download complete pop up message

        Returns: returns True if the element is present

        """
        element = "//p[contains(text(), 'Download complete!')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            return True
        return False

    def check_download_complete_pop_up_absence(self) -> bool:
        """ Check for the absence of download complete pop up message

        Returns: returns True if the element is not present

        """
        element = "//p[contains(text(), 'Download complete!')]"
        if self.check_element_absence(LocatorType.XPath, element, 30):
            return True
        return False

    def click_folder_download(self, folder_name) -> bool:
        """ Performs click action on folder download button

        Args:
            folder_name: Name of the folder to be download

        Returns: returns the result of click action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(f".//span[contains(text(),'{folder_name}')]")
                if folder_title is not None:
                    folder_download_button_div = folder_div.find_element_by_xpath\
                        ("//div[@class='Folder__row Folder__row--expanded']")
                    folder_download_button = folder_download_button_div.find_element_by_xpath\
                        (".button[contains(text(), 'Download')]")
                    if folder_download_button is not None:
                        folder_download_button.click()
                        return True
        return False

    def verify_file_is_downloaded(self, file_name) -> bool:
        """ Verify file is downloaded

        Args:
            file_name: Name of the file to be verify

        Returns: returns the result of verification

        """
        element = "//div[@class='File']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            file_div_list = self.driver.find_elements_by_xpath(element)
            for file_div in file_div_list:
                file_title_div = file_div.find_element_by_xpath(".//div[@id='Tooltip--file']")
                if file_name == file_title_div.get_text().strip():
                    file_download_button = file_div.find_element_by_xpath(".//button[contains(text(), 'Downloaded')]")
                    if file_download_button is not None and file_download_button.is_enabled():
                        return True
        return False

    def verify_folder_and_files_downloaded(self, folder_name) -> bool:
        """ Verify folder and all files inside it is downloaded

        Args:
            folder_name: Name of the folder to be verify

        Returns: returns the result of verification

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(f".//span[contains(text(),'{folder_name}')]")
                if folder_title is not None:
                    folder_download_button_div = folder_div.find_element_by_xpath \
                        (".//div[@class='Folder__row Folder__row--expanded']")
                    folder_download_button = folder_download_button_div.find_element_by_xpath \
                        (".//button[contains(text(), 'Downloaded')]")
                    if folder_download_button is not None:
                        file_div_list = folder_div.find_elements_by_xpath(".//div[@class='File']")
                        for file_div in file_div_list:
                            file_download_button = file_div.find_element_by_xpath\
                                (".//button[contains(text(), 'Downloaded')]")
                            if file_download_button is None:
                                return False
                    else:
                        return False
                else:
                    return False
        return True
