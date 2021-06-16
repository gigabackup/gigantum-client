from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from client_app.helper.local_dataset_helper_utility import DatasetHelperUtility


class DatasetDataComponent(BaseComponent):
    """ Represents one of the components of dataset listing page.

       Holds a set of all locators within the Data tab components on the dataset listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(DatasetDataComponent, self).__init__(driver, component_data)

    def drag_and_drop_text_file_in_data_drop_zone(self, file_name: str, file_content: str) -> bool:
        """Drag and drop the text file into Data drop zone

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

    def drag_and_drop_text_file_in_data_file_browser(self, file_name: str, file_content: str) -> bool:
        """Drag and drop the text file into Data file browser area

        Args:
            file_name: Name of the file
            file_content: Content of the file to be drag

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@data-selenium-id='FileBrowser']")
        if drop_box is not None:
            drop_box.drag_drop_file_in_drop_zone(file_name=file_name, file_content=file_content)
            return True
        return False

    def click_new_folder_button(self) -> bool:
        """ Performs click action on new folder button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'New Folder')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            new_folder_button = self.get_locator(LocatorType.XPath, element)
            if new_folder_button is not None and new_folder_button.element_to_be_clickable():
                new_folder_button.execute_script("arguments[0].click();")
                return True
        return False

    def type_new_folder_name(self, folder_name) -> bool:
        """ Type new folder name

        Args:
            folder_name: Name of the new folder

        Returns: returns the result of folder name input action

        """
        element = "//input[@placeholder='Enter Folder Name']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_name_input = self.get_locator(LocatorType.XPath, element)
            folder_name_input.send_keys(folder_name)
            return True
        return False

    def check_file_uploading_progress_bar_presence(self) -> bool:
        """ Check for the presence of file uploading progress bar

        Returns: returns the result of progress bar checking

        """
        element = "//div[@class='FooterUploadBar--status']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def check_file_uploading_progress_bar_absence(self) -> bool:
        """ Check for the absence of file uploading progress bar

        Returns: returns the result of progress bar checking

        """
        element = "//div[@class='FooterUploadBar--status']"
        if self.check_element_absence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_add_button(self) -> bool:
        """ Performs click action on add button

        Returns: returns the result of click action

        """
        element = "//button[@class='File__btn--round File__btn--add']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            new_folder_add_button = self.get_locator(LocatorType.XPath, element)
            if new_folder_add_button is not None and new_folder_add_button.is_enabled():
                new_folder_add_button.execute_script("arguments[0].click();")
                return True
        return False

    def verify_download_all_files_button_is_enabled(self) -> bool:
        """ Verify all files need to be download

        Returns: returns the result of verification

        """
        element = "//button[contains(text(), 'Download All')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
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
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            file_div_list = self.driver.find_elements_by_xpath(element)
            for file_div in file_div_list:
                file_title_div = file_div.find_element_by_xpath(".//div[@class='File__text']/div")
                if file_name == file_title_div.get_text().strip():
                    file_download_button = file_div.find_element_by_xpath(".//button[contains(text(), 'Download')]")
                    file_download_button.click()
                    return True
        return False

    def click_download_all(self) -> bool:
        """ Performs click action on Download All button

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Download All')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            download_all_button = self.get_locator(LocatorType.XPath, element)
            if download_all_button is not None and download_all_button.is_enabled():
                download_all_button.click()
                return True
        return False

    def verify_all_files_downloaded(self) -> bool:
        """ Verify all files are downloaded

        Returns: returns the result of verification

        """
        element = "//button[@class='Btn__FileBrowserAction Btn--action Btn__FileBrowserAction--download " \
                  "Btn__FileBrowserAction--download--data  Tooltip-data']"
        if self.check_element_presence(LocatorType.XPath, element, 120):
            return True
        return False

    def check_download_complete_pop_up_presence(self) -> bool:
        """ Check for the presence of download complete pop up message

        Returns: returns True if the element is present

        """
        element = "//p[contains(text(), 'Download complete!')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def check_download_complete_pop_up_absence(self) -> bool:
        """ Wait for the absence of download complete pop up message

        Returns: returns True if the element is invisible

        """
        element = "//p[contains(text(), 'Download complete!')]"
        download_complete_pop_up = self.get_locator(LocatorType.XPath, element)
        if download_complete_pop_up.invisibility_of_element_located(120):
            return True
        return False

    def click_folder_download(self, folder_name) -> bool:
        """ Performs click action on folder download button

        Args:
            folder_name: Name of the folder to be download

        Returns: returns the result of click action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == folder_name:
                    folder_download_button = folder_div.find_element_by_xpath\
                        (".//button[contains(text(), 'Download')]")
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
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            file_div_list = self.driver.find_elements_by_xpath(element)
            for file_div in file_div_list:
                file_title_div = file_div.find_element_by_xpath(".//div[@class='File__text']/div")
                if file_name == file_title_div.get_text().strip():
                    file_download_button_element = ".//button[contains(text(), 'Downloaded')]"
                    if self.check_element_presence(LocatorType.XPath, file_download_button_element,
                                                   GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
                        return True
        return False

    def verify_folder_is_downloaded(self, folder_name) -> bool:
        """ Verify folder is downloaded

        Args:
            folder_name: Name of the folder to be verify

        Returns: returns the result of verification

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == folder_name:
                    folder_download_button = folder_div.find_element_by_xpath \
                        (".//button[contains(text(), 'Downloaded')]")
                    if folder_download_button is not None:
                        return True
        return False

    def verify_all_files_in_folder_downloaded(self, folder_name) -> bool:
        """ Verify all files in a folder is downloaded

        Args:
            folder_name: Name of the folder to be verify

        Returns: returns the result of verification

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == folder_name:
                    file_div_list = folder_div.find_elements_by_xpath(".//div[@class='File']")
                    for file_div in file_div_list:
                        file_download_button = file_div.find_element_by_xpath\
                            (".//button[contains(text(), 'Downloaded')]")
                        if file_download_button is None:
                            return False
        return True

    def get_hash_code(self, dataset_title) -> str:
        """ Get git hash code

        Args:
            dataset_title: Title of the dataset

        Returns: returns git hash code

        """
        hash_code = DatasetHelperUtility().get_hash_code(dataset_title)
        return hash_code

    def add_file(self, file_name, file_content, folder_name, dataset_name, hash_code_folder,
                 sub_folder_name: str = None) -> bool:
        """ Add file into folders

        Args:
            file_name: Name of the file to be add
            file_content: Content of the file to be add
            folder_name: Name of the folder in which file to be added
            dataset_name: Name of the dataset
            hash_code_folder: Folder in which files need to be placed
            sub_folder_name: Name of the sub folder

        Returns: returns the result of file addition

        """
        return DatasetHelperUtility().add_file(file_name, file_content, folder_name, dataset_name, hash_code_folder
                                                    , sub_folder_name)

    def click_new_sub_folder_button(self, parent_folder_name) -> bool:
        """ Performs click action on new sub folder button

        Args:
            parent_folder_name: Name of the parent folder

        Returns: returns the result of click action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == parent_folder_name:
                    sub_folder_button = folder_div.find_element_by_xpath(".//button[@class='ActionsMenu__item Btn "
                                                                         "Btn--fileBrowser Btn--round Btn__addFolder']")
                    sub_folder_button.execute_script("arguments[0].click();")
                    return True
        return False

    def type_sub_folder_name(self, parent_folder_name, sub_folder_name) -> bool:
        """ Type new sub folder name

        Args:
            parent_folder_name: Name of the parent folder
            sub_folder_name: Name of the sub folder

        Returns: returns the result of sub folder name input action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == parent_folder_name:
                    sub_folder_input = folder_div.find_element_by_xpath(".//input[@placeholder='Enter Folder Name']")
                    if sub_folder_input is not None:
                        sub_folder_input.send_keys(sub_folder_name)
                        return True
        return False

    def click_sub_folder_add_button(self, parent_folder_name) -> bool:
        """ Performs click action on sub folder add button

        Returns: returns the result of click action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == parent_folder_name:
                    sub_folder_add_button = folder_div.find_element_by_xpath("//div[@class='Folder__child']/div/div[3]/"
                                                                             "button[2]")
                    if sub_folder_add_button is not None:
                        sub_folder_add_button.execute_script("arguments[0].click();")
                        return True
        return False

    def click_on_folder(self, folder_name):
        """ Performs click action on folder

        Args:
            folder_name: Name of the folder

        Returns: returns the result of click action

        """
        element = "//div[@class='Folder']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            folder_div_list = self.driver.find_elements_by_xpath(element)
            for folder_div in folder_div_list:
                folder_title = folder_div.find_element_by_xpath(".//div[@class='Folder__name']/div[1]").text
                if folder_title == folder_name:
                    folder_div.click()
                    return True
        return False

    def add_binary_file_to_root(self, file_name, size_in_mb, dataset_name, hash_code_folder,
                                random_contents=False) -> bool:
        """ Add binary file into root directory

        Args:
            file_name: Name of the file
            size_in_mb: Size of the file in MBs
            hash_code_folder: Name of the hash code folder
            dataset_name: Name of the dataset
            random_contents: True for random file, False for all 0's

        Returns: returns the result of file creation

        """
        return DatasetHelperUtility().add_binary_file_to_root(file_name, size_in_mb, dataset_name, hash_code_folder,
                                                              random_contents)

    def add_file_to_root(self, file_name, file_content, dataset_name, hash_code_folder) -> bool:
        """ Add file

        Args:
            file_name: Name of the file
            file_content: Size of the file
            hash_code_folder: Name of the hash code folder
            dataset_name: Name of the dataset

        Returns: returns the result of file add

        """
        return DatasetHelperUtility().add_file_to_root(file_name, file_content, dataset_name, hash_code_folder)

    def update_file_content(self, file_name, file_content, dataset_name, hash_code_folder) -> bool:
        """ Update file content

        Args:
            file_name: Name of the file to be add
            file_content: Content of the file to be add
            dataset_name: Name of the dataset
            hash_code_folder: Folder in which files need to be placed

        Returns: returns the result of file content update operation

        """
        return DatasetHelperUtility().update_file_content(file_name, file_content, dataset_name, hash_code_folder)

    def check_data_tab_window_opened(self) -> bool:
        """ Check for the data tab window element

        Returns: returns the result of data tab window element check

        """
        element = "//h4[contains(text(), 'Files')]"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def verify_dataset_file_cache(self, dataset_name) -> bool:
        """ Check whether the dataset file cache exist or not

        Args:
            dataset_name: Name of the dataset to be verified

        Returns: returns the result of file verification

        """
        return DatasetHelperUtility().verify_dataset_file_cache(dataset_name)
