"""Test call for Create and publish a dataset"""
import pytest

from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.pages.login.login_factory import LoginFactory
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.dataset_listing.dataset_listing_page import DatasetListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.helper.dataset_utility import DatasetUtility
from tests.constants_enums.constants_enums import ProjectConstants
import time
from tests.test_fixtures import clean_up_dataset
from tests.test_fixtures import server_data_fixture


@pytest.mark.createPublishDatasetTest
class TestCreatePublishDataset:
    """Includes test methods for basic dataset creation, publish and its dependent tests"""

    @pytest.mark.run(order=1)
    def test_log_in_success(self, server_data_fixture):
        """ Test method to check the successful log-in."""
        landing_page = LandingPage(self.driver)
        ProjectHelperUtility().set_server_details(server_data_fixture)
        landing_page.landing_component.click_server(server_data_fixture.server_name)
        login_page = LoginFactory().load_login_page(server_data_fixture.login_type, self.driver)
        assert login_page.check_login_page_title()
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                   LoginUser.User1)
        project_list = login_page.login(user_credentials.user_name, user_credentials.password)
        assert project_list.project_listing_component.get_project_title() == "Projects"

    @pytest.mark.depends(on=['test_log_in_success'])
    def test_create_publish_dataset(self, clean_up_dataset):
        """Test method to create and publish a dataset"""

        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Create dataset
        is_success_msg = dataset_utility.create_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load dataset Listing Page
        dataset_list = DatasetListingPage(self.driver)
        assert dataset_list, "Could not load Dataset Listing Page"

        # Get dataset title
        dataset_title = dataset_list.project_menu_component.get_title()
        assert dataset_title is not None, "Could not get the dataset title"

        # Add files
        self.add_files(dataset_list, dataset_title)

        # Publish Dataset
        is_success_msg = dataset_utility.publish_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Get hash code
        hash_code = dataset_list.dataset_data_component.get_hash_code(dataset_title)
        assert hash_code is not None, "Could not get hash code"

        # Update file 'file1.txt'
        is_added = dataset_list.dataset_data_component.update_file_content('file1.txt', 'updated', dataset_title,
                                                                        hash_code)
        assert is_added is not None, "Could not update file 'file1.txt'"

        # Sync dataset
        self.sync_dataset(dataset_list)

        # Delete dataset locally
        is_success_msg = dataset_utility.delete_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Import dataset
        self.import_dataset(dataset_list, dataset_title)

        # Verify files and download
        self.verify_files_and_download(dataset_list)

        # Delete dataset locally
        is_success_msg = dataset_utility.delete_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete dataset from server
        self.delete_dataset_from_server(dataset_list, dataset_title)

    def add_files(self, dataset_list, dataset_title):
        """Logical separation of add files

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the current dataset

        """
        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"

        # Check data tab window opened
        is_checked = dataset_list.dataset_data_component.check_data_tab_window_opened()
        assert is_checked, "Could not verify data tab window opened"

        # Click on create new folder button
        is_clicked = dataset_list.dataset_data_component.click_new_folder_button()
        assert is_clicked, "Could not click 'New Folder' button"

        # Type new folder title 'folder1'
        is_typed = dataset_list.dataset_data_component.type_new_folder_name('folder1')
        assert is_typed, "Could not type new folder title 'folder1'"

        # Click on new folder add button
        is_clicked = dataset_list.dataset_data_component.click_add_button()
        assert is_clicked, "Could not click new folder add button"

        time.sleep(.5)

        # Click on create new folder button
        is_clicked = dataset_list.dataset_data_component.click_new_folder_button()
        assert is_clicked, "Could not click 'New Folder' button"

        # Type new folder title 'folder2'
        is_typed = dataset_list.dataset_data_component.type_new_folder_name('folder2')
        assert is_typed, "Could not type new folder title 'folder2'"

        # Click on new folder add button
        is_clicked = dataset_list.dataset_data_component.click_add_button()
        assert is_clicked, "Could not click new folder add button"

        time.sleep(.5)

        # Click on create new sub folder button for 'folder2'
        is_clicked = dataset_list.dataset_data_component.click_new_sub_folder_button('folder2')
        assert is_clicked, "Could not click 'New Folder' button on 'folder2'"

        # Type new sub folder title 'folder2-1' for folder 'folder2'
        is_typed = dataset_list.dataset_data_component.type_sub_folder_name('folder2', 'folder2-1')
        assert is_typed, "Could not type new folder title 'folder2-1' for folder 'folder2'"

        # Click on new sub folder add button
        is_clicked = dataset_list.dataset_data_component.click_sub_folder_add_button('folder2')
        assert is_clicked, "Could not click new sub folder add button"

        # Added a wait to get the updated hash code
        time.sleep(3)

        # Get hash code
        hash_code = dataset_list.dataset_data_component.get_hash_code(dataset_title)
        assert hash_code is not None, "Could not get hash code"

        # Add file 'folder1-file1.txt' into folder 1
        is_added = dataset_list.dataset_data_component.add_file('folder1-file1.txt', 'created1', 'folder1',
                                                                dataset_title,
                                                                hash_code)
        assert is_added is not None, "Could not add file 'folder1-file1.txt' into folder 1"

        # Add file 'folder1-file2.txt' into folder 1
        is_added = dataset_list.dataset_data_component.add_file('folder1-file2.txt', 'created2', 'folder1',
                                                                dataset_title,
                                                                hash_code)
        assert is_added is not None, "Could not add file 'folder1-file2.txt' into folder 1"

        # Add file 'folder1-file3.txt' into folder 1
        is_added = dataset_list.dataset_data_component.add_file('folder1-file3.txt', 'created3', 'folder1',
                                                                dataset_title,
                                                                hash_code)
        assert is_added is not None, "Could not add file 'folder1-file3.txt' into folder 1"

        # Add file 'folder1-file4.txt' into folder 1
        is_added = dataset_list.dataset_data_component.add_file('folder1-file4.txt', 'created4', 'folder1',
                                                                dataset_title,
                                                                hash_code)
        assert is_added is not None, "Could not add file 'folder1-file4.txt' into folder 1"

        # Add file 'folder2-1-file1.txt' into sub folder 'folder2-1'
        is_added = dataset_list.dataset_data_component.add_file('folder2-1-file1.txt', 'same contents', 'folder2',
                                                                dataset_title,
                                                                hash_code, 'folder2-1')
        assert is_added is not None, "Could not add file 'folder2-1-file1.txt' into sub folder 'folder2-1"

        # Add file 'folder2-1-file2.txt' into sub folder 'folder2-1'
        is_added = dataset_list.dataset_data_component.add_file('folder2-1-file2.txt', 'same contents', 'folder2',
                                                                dataset_title,
                                                                hash_code, 'folder2-1')
        assert is_added is not None, "Could not add file 'folder2-1-file2.txt' into sub folder 'folder2-1"

        # Add file 'folder2-1-file3.txt' into sub folder 'folder2-1'
        is_added = dataset_list.dataset_data_component.add_file('folder2-1-file3.txt', 'same contents', 'folder2',
                                                                dataset_title,
                                                                hash_code, 'folder2-1')
        assert is_added is not None, "Could not add file 'folder2-1-file3.txt' into sub folder 'folder2-1"

        # Add file 'folder2-1-file4.txt' into sub folder 'folder2-1'
        is_added = dataset_list.dataset_data_component.add_file('folder2-1-file4.txt', 'same contents', 'folder2',
                                                                dataset_title,
                                                                hash_code, 'folder2-1')
        assert is_added is not None, "Could not add file 'folder2-1-file4.txt' into sub folder 'folder2-1"

        # Add binary file 'large.bin' into root directory
        is_added = dataset_list.dataset_data_component.add_binary_file_to_root('large.bin', 100, dataset_title,
                                                                               hash_code, random_contents=True)
        assert is_added is not None, "Could not add file"

        # Add binary file 'large-compress.bin' into root directory
        is_added = dataset_list.dataset_data_component.add_binary_file_to_root('large-compress.bin', 100, dataset_title,
                                                                               hash_code, random_contents=False)
        assert is_added is not None, "Could not add file"

        # A permission issue was raised for drag and drop.
        # Solved temporarily by reloading the page with a few clicks on the page.
        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"

        # Drag and drop file into file browser area is not reflecting with out time sleep
        time.sleep(5)

        # Drag and drop text file 'file1.txt' with contents 'created'
        is_dropped = dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_file_browser('file1.txt',
                                                                                                      'created')
        assert is_dropped, "Could not drop 'file1.txt' into data drop zone"

        # Check for the presence of file upload progress bar
        is_checked = dataset_list.dataset_data_component.check_file_uploading_progress_bar_presence()
        assert is_checked, "Could not found the presence of file upload progress bar"

        # Check for the absence of file upload progress bar
        is_checked = dataset_list.dataset_data_component.check_file_uploading_progress_bar_absence()
        assert is_checked, "Could not get the absence of file upload progress bar"

    def sync_dataset(self, dataset_list):
        """Logical separation of sync dataset

        Args:
            dataset_list: The page with UI elements

        """
        # Click on Sync button
        is_clicked = dataset_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Check for the sync button is enabled
        is_checked = dataset_list.project_menu_component.check_sync_button_is_enabled()
        assert is_checked, "Could not check the sync button is enabled"

    def import_dataset(self, dataset_list, dataset_title):
        """Logical separation of import dataset

        Args:
            dataset_title: Title of the dataset
            dataset_list: The page with UI elements

        """
        # Click server tab
        is_clicked = dataset_list.server_component.click_server_tab()
        assert is_clicked, "Could not click server tab"

        # Verify dataset in server page
        is_verified = dataset_list.server_component.verify_title_in_server(dataset_title)
        assert is_verified, "Could not verify dataset in server"

        # Click import button in server page
        is_clicked = dataset_list.server_component.click_import_button(dataset_title)
        assert is_clicked, "Could not click import button in server page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

    def verify_files_and_download(self, dataset_list):
        """Logical separation of verify files and download

        Args:
            dataset_list: The page with UI elements

        """
        # Small sleep to make sure everything is loaded before clicking on data tab
        time.sleep(1)

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"

        # Small sleep to make sure everything is loaded before checking button state
        time.sleep(1)

        # Verify all files need to be download
        is_verified = dataset_list.dataset_data_component.verify_download_all_files_button_is_enabled()
        assert is_verified, "Could not verify all the files need to be download"

        # Download file 'file1.txt'
        is_clicked = dataset_list.dataset_data_component.click_file_download("file1.txt")
        assert is_clicked, "Could not click download button for 'file.txt'"

        # Check for the presence of download complete pop up message for 'file1.txt'
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for 'file1.txt'"

        # Check download complete pop up message for 'file1.txt' is closed
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_absence()
        assert is_checked, "Download complete pop up is not closed for 'file1.txt'"

        # Verify 'file.txt' is downloaded
        is_verified = dataset_list.dataset_data_component.verify_file_is_downloaded("file1.txt")
        assert is_verified, "Could not verify 'file.txt' is downloaded"

        # Download folder 'folder1'
        is_clicked = dataset_list.dataset_data_component.click_folder_download("folder1")
        assert is_clicked, "Could not click download button for 'folder1'"

        # Check for the presence of download complete pop up message for 'folder1'
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for 'folder1'"

        # Check download complete pop up message for 'folder1' is closed
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_absence()
        assert is_checked, "Download complete pop up is not closed for 'folder1t'"

        # Verify folder 'folder1' is downloaded
        is_verified = dataset_list.dataset_data_component.verify_folder_is_downloaded("folder1")
        assert is_verified, "'folder1' is not downloaded"

        # Click on folder 'folder1'
        is_clicked = dataset_list.dataset_data_component.click_on_folder("folder1")
        assert is_clicked, "Could not click on 'folder1'"

        # Verify all files in 'folder1' downloaded
        is_verified = dataset_list.dataset_data_component.verify_all_files_in_folder_downloaded("folder1")
        assert is_verified, "Files in 'folder1' is not downloaded"

        # Click on folder 'folder2'
        is_clicked = dataset_list.dataset_data_component.click_on_folder("folder2")
        assert is_clicked, "Could not click on 'folder2'"

        # Click on sub folder 'folder2-1'
        is_clicked = dataset_list.dataset_data_component.click_on_folder("folder2-1")
        assert is_clicked, "Could not click on sub folder 'folder2-1'"

        # Download file 'folder2-1-file3.txt'
        is_clicked = dataset_list.dataset_data_component.click_file_download("folder2-1-file3.txt")
        assert is_clicked, "Could not click download button for 'folder2-1-file3.txt'"

        # Check for the presence of download complete pop up message for 'folder2-1-file3.txt'
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for 'folder2-1-file3.txt'"

        # Check download complete pop up message for 'folder2-1-file3.txt' is closed
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_absence()
        assert is_checked, "Download complete pop up is not closed for 'folder2-1-file3.txt'"

        # Verify all files in folder 'folder2-1' is downloaded
        is_verified = dataset_list.dataset_data_component.verify_all_files_in_folder_downloaded("folder2-1")
        assert is_verified, "Files in 'folder2-1' is not downloaded"

        # Click Download All button
        is_clicked = dataset_list.dataset_data_component.click_download_all()
        assert is_clicked, "Could not click 'Download All' button"

        # Check for the presence of download complete pop up message
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for Download All"

        # Verify all files are downloaded
        is_verified = dataset_list.dataset_data_component.verify_all_files_downloaded()
        assert is_verified, "Could not verify all files are downloaded"

    def delete_dataset_from_server(self, dataset_list, dataset_title):
        """ Logical separation of delete dataset from server

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the current dataset

        """
        # Click server tab
        is_clicked = dataset_list.server_component.click_server_tab()
        assert is_clicked, "Could not click server tab"

        # Verify dataset in server page
        is_verified = dataset_list.server_component.verify_title_in_server(dataset_title)
        assert is_verified, "Could not verify dataset in server"

        # Click delete button in server page
        is_clicked = dataset_list.server_component.click_delete_button(dataset_title)
        assert is_clicked, "Could not click delete button in server page"

        # Get dataset title from delete dataset window in server page
        dataset_name = dataset_list.server_component.get_title()
        assert dataset_name is not None, "Could not get dataset title in server page"

        # Input dataset title in delete window on server page
        is_typed = dataset_list.server_component.input_title(dataset_name)
        assert is_typed, "Could not type dataset title in delete window on server page"

        # Click delete dataset button in delete window on server page
        is_clicked = dataset_list.server_component.click_delete_button_on_window()
        assert is_clicked, "Could not click delete dataset button in delete window on server page"

        # Verify delete modal close
        is_verified = dataset_list.server_component.verify_delete_modal_closed(30)
        assert is_verified, "Could not close delete modal"

        # Verify dataset is not exist in server page
        is_verified = dataset_list.server_component.verify_title_in_server(dataset_title)
        assert not is_verified, "Dataset is still exist in the server"

        # wait ~5 seconds to guarantee server side deletion completes
        time.sleep(5)

        # Refresh the server page
        is_clicked = dataset_list.server_component.click_server_tab()
        assert is_clicked, "Could not click server tab"

        # Verify dataset is not exist in server page
        is_verified = dataset_list.server_component.verify_title_in_server(dataset_title)
        assert not is_verified, "Dataset is still exist in the server page"
