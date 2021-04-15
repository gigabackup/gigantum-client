import random
import time
import string

from client_app.pages.dataset_listing.dataset_listing_page import DatasetListingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from selenium import webdriver
from tests.constants_enums.constants_enums import ProjectConstants
from client_app.pages.jupyter_lab.jupyter_lab_page import JupyterLabPage
from tests.helper.project_utility import ProjectUtility


class DatasetUtility:
    def create_dataset(self, driver: webdriver) -> str:
        """Logical separation of create dataset functionality"""
        # Create a dataset

        # Load Project Listing Page
        project_list = ProjectListingPage(driver)
        if not project_list:
            return "Could not load Project Listing Page"

        # Closes the guide
        project_utility = ProjectUtility()
        guide_close_msg = project_utility.close_guide(project_list)
        if guide_close_msg != ProjectConstants.SUCCESS.value:
            return guide_close_msg

        # Load dataset Listing Page
        dataset_list = DatasetListingPage(driver)
        if not dataset_list:
            return "Could not load 'Dataset Listing' Page."

        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        if not is_clicked:
            return "Could not click dataset menu."

        # Click on "Create New"
        is_clicked = dataset_list.dataset_listing_component.click_create_new_dataset_button()
        if not is_clicked:
            return "Could not click 'Create New' button."

        # Enter dataset title-(unique random name) and description
        # UUID is not given now, since it creates big string
        # This can be changed along with upcoming text cases
        rand_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        dataset_title = f"d-{rand_string}"
        is_dataset_title_typed = dataset_list.dataset_listing_component.type_dataset_title(dataset_title)
        is_dataset_desc_typed = dataset_list.dataset_listing_component.type_new_dataset_desc_textarea(
            f"{dataset_title} -> Description ")
        if not is_dataset_title_typed:
            return "Could not type dataset title."
        if not is_dataset_desc_typed:
            return "Could not type dataset description."

        # Click "Create dataset" button
        is_clicked = dataset_list.dataset_listing_component.click_create_dataset_button()
        if not is_clicked:
            return "Could not click create dataset button."

        return ProjectConstants.SUCCESS.value

    def delete_dataset(self, driver: webdriver) -> str:
        """ Logical separation of delete dataset functionality

        Args:
            driver: webdriver instance
        """
        # Delete a local dataset
        # Load dataset Listing Page
        dataset_list = DatasetListingPage(driver)
        if not dataset_list:
            return "Could not load Dataset Listing Page"

        # Click project menu button
        is_clicked = dataset_list.project_menu_component.click_project_menu_button()
        if not is_clicked:
            return "Could not click project menu button"

        # Click delete dataset menu
        is_checked = dataset_list.dataset_menu_component.click_delete_dataset_menu()
        if not is_checked:
            return "Could not click delete dataset menu"

        # Get dataset title from delete dataset window
        dataset_title = dataset_list.dataset_delete_component.get_dataset_title()
        if dataset_title is None:
            return "Could not get dataset title"

        # Input dataset title
        is_typed = dataset_list.dataset_delete_component.input_dataset_title(dataset_title)
        if not is_typed:
            return "Could not type dataset title"

        # Click delete dataset button
        is_clicked = dataset_list.dataset_delete_component.click_delete_button()
        if not is_clicked:
            return "Could not click delete dataset button"

        return ProjectConstants.SUCCESS.value

    def verify_file_content_in_jupyter_lab(self, driver: webdriver, files_details_list: list) -> str:
        """ Logical separation of verify file content using jupyter lab

        Args:
            driver: web driver instance
            files_details_list: List of tuples with file_details
        """
        # Load Jupyter Lab page Page
        jupyter_lab_page = JupyterLabPage(driver)
        if not jupyter_lab_page:
            return "Could not load Jupyter Lab Page"

        # Click on Jupyter Lab button
        is_clicked = jupyter_lab_page.click_jupyterlab_div()
        if not is_clicked:
            return "Could not click Jupyter Lab button"

        # Wait for new tab to open with new url
        is_url_loaded = jupyter_lab_page.wait_for_url_in_new_tab("/lab", 1, 60)
        if not is_url_loaded:
            return "Could not open new window"

        # Iterate through list of file_details
        for file_details in files_details_list:
            file_content_verification_result = self.__verify_file_content(jupyter_lab_page, file_details)
            if file_content_verification_result != ProjectConstants.SUCCESS.value:
                return file_content_verification_result

        jupyter_lab_page.close_tab("/lab", 0)

        # Click on container status button to stop container
        is_clicked = jupyter_lab_page.click_container_status()
        if not is_clicked:
            return "Could not click container status"

        # Monitor container status to go through running -> stopped
        jupyter_lab_page.move_to_element()
        is_status_changed = jupyter_lab_page.monitor_container_status("Stopped", 60)
        if not is_status_changed:
            return "Could not get Stopped status"

        return ProjectConstants.SUCCESS.value

    def __verify_file_content(self, jupyter_lab_page, file_details):
        """ Verify file content

        Args:
            jupyter_lab_page: Instance of JupyterLabPage
            file_details: Tuple contain file details

        Returns:

        """
        # Click folder path icon
        is_clicked = jupyter_lab_page.click_folder_path_icon()
        if not is_clicked:
            return "Could not click folder path icon in Jupyter Lab"

        # Double click on folder
        is_clicked = jupyter_lab_page.click_folder(file_details.folder_name)
        if not is_clicked:
            return "Could not select the folder"

        # Double click on dataset folder
        is_clicked = jupyter_lab_page.click_folder(file_details.dataset_name)
        if not is_clicked:
            return "Could not select the dataset folder"

        # Choose the file
        is_selected = jupyter_lab_page.click_file(file_details.file_name)
        if not is_selected:
            return "Could not select the file"

        # Verify file content
        time.sleep(1)
        is_verified = jupyter_lab_page.verify_file_content(file_details.file_content)
        if not is_verified:
            return "Could not verify the file contents"

        return ProjectConstants.SUCCESS.value

    def publish_dataset(self, driver: webdriver):
        """Logical separation of publish dataset functionality

        Args:
            driver: The page with UI elements

        """
        # Load dataset Listing Page
        dataset_list = DatasetListingPage(driver)
        if not dataset_list:
            return "Could not load Dataset Listing Page"

        # Click on publish button
        is_clicked = dataset_list.project_menu_component.click_publish_button()
        if not is_clicked:
            return "Could not click publish button"

        # Enable private mode in publish window
        is_enabled = dataset_list.project_menu_component.enable_private_mode()
        if not is_enabled:
            return "Could not enable private mode in publish window"

        # Click on publish button on publish window
        is_clicked = dataset_list.project_menu_component.click_publish_window_button()
        if not is_clicked:
            return "Could not click publish button on project publish window"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        if not is_checked:
            return "Could not found private lock icon presence"

        return ProjectConstants.SUCCESS.value
