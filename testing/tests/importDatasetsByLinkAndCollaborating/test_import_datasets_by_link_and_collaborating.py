"""Test call for importing datasets by link and collaborating"""
import pytest
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.dataset_listing.dataset_listing_page import DatasetListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.helper.dataset_utility import DatasetUtility
from tests.helper.project_utility import ProjectUtility
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_dataset
from tests.test_fixtures import clean_up_remote_dataset
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture
import time


@pytest.mark.importDatasetsByLinkAndCollaborating
class TestImportDatasetsByLinkAndCollaborating:
    """Includes test methods for basic dataset creation and importing datasets by link and collaborating"""

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
    def test_import_datasets_by_link_and_collaborating(self, clean_up_dataset, clean_up_remote_dataset,
                                                       server_data_fixture):
        """Test method to importing datasets by link and collaborating"""
        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Instance of ProjectUtility class
        project_utility = ProjectUtility()

        # Create dataset
        is_success_msg = dataset_utility.create_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load dataset Listing Page
        dataset_list = DatasetListingPage(self.driver)
        assert dataset_list, "Could not load Dataset Listing Page"

        # Get dataset title
        dataset_title = dataset_list.project_menu_component.get_title()
        assert dataset_title is not None, "Could not get the dataset title"

        # Set dataset details into 'clean_up_remote_dataset' fixture
        dataset_details = {'dataset_name': dataset_title, 'driver': self.driver}
        clean_up_remote_dataset.update(dataset_details)

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"
        time.sleep(5)

        # Drag and drop text file with contents "created"
        is_dropped = dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_drop_zone('file1', 'created')
        assert is_dropped, "Could not drop file1 into data drop zone"

        # Publish Dataset
        is_success_msg = dataset_utility.publish_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Click project menu button
        is_clicked = dataset_list.project_menu_component.click_project_menu_button()
        assert is_clicked, "Could not click project menu button"

        # Get import URL
        import_url = dataset_list.project_menu_component.get_import_url()
        assert import_url is not None, "Could not get import URL"

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Try to import dataset and expect import error
        self.try_to_import_dataset(dataset_list, import_url)

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Add user2 as collaborator
        is_success_msg = dataset_utility.add_collaborator(self.driver, user2_credentials.display_name, 'Read')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Import dataset and download file
        self.import_dataset_and_download_file(dataset_list, import_url)

        # Try to edit dataset and expect error
        self.try_to_edit_dataset(dataset_list)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Update collaborator permission
        self.update_collaborator_permission(dataset_list, dataset_title, user2_credentials.display_name, 'Admin')

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Edit dataset by adding file2
        self.edit_dataset_and_sync(dataset_list, dataset_title)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Sync and verify file
        self.sync_and_verify_file(dataset_list, dataset_title)

    def try_to_import_dataset(self, dataset_list, import_url):
        """Logical separation of try to import dataset functionality

        Args:
            dataset_list: The page with UI elements
            import_url: URL of the dataset to be import

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Click import existing button
        is_clicked = dataset_list.dataset_listing_component.click_import_existing_dataset_button()
        assert is_clicked, "Could not click import existing button"

        # Type import URL into input area
        is_typed = dataset_list.dataset_listing_component.type_dataset_import_url(import_url)
        assert is_typed, "Could not type import URL"

        # Click import dataset button
        is_clicked = dataset_list.dataset_listing_component.click_import_dataset_button()
        assert is_clicked, "Could not click import dataset button"

        # Verify dataset import error pop up is shown
        is_verified = dataset_list.dataset_listing_component.verify_dataset_import_error()
        assert is_verified, "Could not verify dataset import error"

    def import_dataset_and_download_file(self, dataset_list, import_url):
        """Logical separation of import dataset and download file functionality

        Args:
            dataset_list: The page with UI elements
            import_url: URL of the dataset to be import

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Click import existing button
        is_clicked = dataset_list.dataset_listing_component.click_import_existing_dataset_button()
        assert is_clicked, "Could not click import existing button"

        # Type import URL into input area
        is_typed = dataset_list.dataset_listing_component.type_dataset_import_url(import_url)
        assert is_typed, "Could not type import URL"

        # Click import dataset button
        is_clicked = dataset_list.dataset_listing_component.click_import_dataset_button()
        assert is_clicked, "Could not click import dataset button"

        # Verify dataset imported successfully
        is_verified = dataset_list.dataset_listing_component.verify_dataset_import_success()
        assert is_verified, "Could not verify dataset imported successfully"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"
        time.sleep(5)

        # Download file 'file1.txt'
        is_clicked = dataset_list.dataset_data_component.click_file_download("file1")
        assert is_clicked, "Could not click download button for 'file.txt'"

        # Check for the presence of download complete pop up message for 'file1.txt'
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for 'file1.txt'"

        # Check download complete pop up message for 'file1.txt' is closed
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_absence()
        assert is_checked, "Download complete pop up is not closed for 'file1.txt'"

        # Verify 'file.txt' is downloaded
        is_verified = dataset_list.dataset_data_component.verify_file_is_downloaded("file1")
        assert is_verified, "Could not verify 'file.txt' is downloaded"

    def try_to_edit_dataset(self, dataset_list):
        """Logical separation of try to edit dataset functionality

        Args:
            dataset_list: The page with UI elements

        """
        # Drag and drop text file with contents "created"
        dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_file_browser('file2', 'created')

        # Verify dataset permission error pop up window is shown or not
        is_verified = dataset_list.dataset_listing_component.verify_dataset_permission_error()
        assert is_verified, "Could not verify dataset permission error pop up window"

    def update_collaborator_permission(self, dataset_list, dataset_title, collaborator_name, collaborator_permission):
        """Logical separation of update collaborator functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the current dataset
            collaborator_name: Name of the collaborator
            collaborator_permission: Collaborator permission

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click on Collaborators button
        is_clicked = dataset_list.project_menu_component.click_collaborators_button()
        assert is_clicked, "Could not click Collaborators button"

        # Update collaborator permission
        is_clicked = dataset_list.collaborator_modal_component.update_collaborator_permission(
            collaborator_name, collaborator_permission)
        assert is_clicked, "Could not update Collaborators permission"

        # Click on collaborator modal close button
        is_clicked = dataset_list.collaborator_modal_component.click_collaborator_modal_close()
        assert is_clicked, "Could not close collaborator modal"

    def edit_dataset_and_sync(self, dataset_list, dataset_title):
        """Logical separation of edit dataset and sync functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the current dataset

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"
        time.sleep(5)

        # Drag and drop text file file2 with contents "created"
        is_dropped = dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_file_browser('file2',
                                                                                                      'created')
        assert is_dropped, "Could not drop file2 into data drop zone"

        # Click on Sync button
        is_clicked = dataset_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Verify sync complete pop up shown or not
        is_verified = dataset_list.project_menu_component.check_upload_complete_pop_up_presence()
        assert is_verified, "Could not verify sync complete pop up window"

        # Check for the sync button is enabled
        is_checked = dataset_list.project_menu_component.check_sync_button_is_enabled()
        assert is_checked, "Could not check the sync button is enabled"

    def sync_and_verify_file(self, dataset_list, dataset_title):
        """Logical separation of edit dataset and sync functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the current dataset

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"
        time.sleep(5)

        # Click on Sync button
        is_clicked = dataset_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Verify sync complete pop up shown or not
        is_verified = dataset_list.project_menu_component.check_sync_complete_pop_up_presence()
        assert is_verified, "Could not verify sync complete pop up window"

        # Check for the sync button is enabled
        is_checked = dataset_list.project_menu_component.check_sync_button_is_enabled()
        assert is_checked, "Could not check the sync button is enabled"

        # Download file 'file2.txt'
        is_clicked = dataset_list.dataset_data_component.click_file_download("file2")
        assert is_clicked, "Could not click download button for 'file2.txt'"

        # Check for the presence of download complete pop up message for 'file2.txt'
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Download complete pop up is not present for 'file2.txt'"

        # Check download complete pop up message for 'file2.txt' is closed
        is_checked = dataset_list.dataset_data_component.check_download_complete_pop_up_absence()
        assert is_checked, "Download complete pop up is not closed for 'file2.txt'"

        # Verify 'file2.txt' is downloaded
        is_verified = dataset_list.dataset_data_component.verify_file_is_downloaded("file2")
        assert is_verified, "Could not verify 'file2.txt' is downloaded"


