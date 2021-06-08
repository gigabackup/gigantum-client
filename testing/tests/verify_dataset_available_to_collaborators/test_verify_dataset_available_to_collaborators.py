"""Test call for verifying dataset added post-import becomes available to collaborators"""
import time
import pytest
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.pages.dataset_listing.dataset_listing_page import DatasetListingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from tests.helper.dataset_utility import DatasetUtility
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from framework.factory.models_enums.constants_enums import LoginUser
from collections import namedtuple
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project, clean_up_remote_dataset, clean_up_remote_project, clean_up_dataset
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.verifyDatasetPostImportedAvailableToCollaborators
class TestVerifyDatasetAvailableToCollaborators:
    """Includes test methods for verifying dataset added post-import becomes available to collaborators"""

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
    def test_verify_dataset_available_to_collaborators(self, clean_up_project, server_data_fixture, clean_up_dataset,
                                                       clean_up_remote_project, clean_up_remote_dataset):
        """Test method to verifying dataset added post-import becomes available to collaborators"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Publish project
        project_utility = ProjectUtility()
        is_success_msg = project_utility.publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Set project details into 'clean_up_remote_project' fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Add user2 as collaborator
        dataset_utility = DatasetUtility()
        is_success_msg = dataset_utility.add_collaborator(self.driver, user2_credentials.display_name, 'Write')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Switch User
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture )
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Import Project
        is_success_msg = project_utility.import_project(self.driver, project_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch User
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Create dataset
        dataset_utility = DatasetUtility()
        is_success_msg = dataset_utility.create_dataset(self.driver, is_guide=False)
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
        time.sleep(6)

        # Drag and drop text file with contents "created"
        is_dropped = dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_drop_zone('file1', 'created')
        assert is_dropped, "Could not drop file1 into data drop zone"

        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Select project
        is_clicked = dataset_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Link dataset
        is_success_msg = dataset_utility.link_dataset(self.driver, dataset_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Sync project
        self.sync_project(dataset_list)

        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Add user2 as dataset collaborator
        dataset_utility = DatasetUtility()
        is_success_msg = dataset_utility.add_collaborator(self.driver, user2_credentials.display_name, 'Read')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Switch User
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Select project
        is_clicked = dataset_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click on Sync button
        is_clicked = project_list.project_menu_component.click_pull_button()
        assert is_clicked, "Could not click Sync button"

        # Verify sync complete pop up shown or not
        is_verified = project_list.project_menu_component.check_upload_complete_pop_up_presence()
        assert is_verified, "Could not verify sync complete pop up window"

        # Check for the sync button is enabled
        is_checked = project_list.project_menu_component.check_sync_button_is_enabled()
        assert is_checked, "Could not check the sync button is enabled"

        # Click on Input Data tab
        is_clicked = project_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click on Input Data tab"

        # Verify dataset is present
        is_clicked = project_list.code_input_output_component.verify_dataset_is_present(dataset_title)
        assert is_clicked, "Could not verify dataset in Input Data tab"

        # Click download all button on input data tab
        is_clicked = dataset_list.code_input_output_data_component.click_input_download_all_button()
        assert is_clicked, "Could not click on download all button on input data tab"

        # Check for the presence of download complete pop up
        is_checked = dataset_list.code_input_output_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Could not check for the presence of download complete pop up window"

        # Verify files are downloaded
        is_verified = dataset_list.code_input_output_data_component.verify_files_are_downloaded()
        assert is_verified, "Could not verify files are downloaded"

        # Verify file content in input folder
        file_details = namedtuple('file_details', ('folder_name', 'dataset_name', 'file_name', 'file_content'))
        file1_details = file_details('input', dataset_title, 'file1', 'created')
        verification_message = dataset_utility.verify_file_content_in_jupyter_lab(self.driver, [file1_details])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Verify dataset auto imported
        self.verify_dataset_auto_imported(project_list, dataset_title)

        # This is a temporary solution- switch user2 to user1 (dataset owner).
        # The clean up in the teardown fixture needs to remove the remote dataset. This can be achieved only by logging
        # in as the owner of the dataset.
        # Will take up a long term fix later as:
        # In cleanup fixture get the owner of the dataset and if needed re-login as the owner.
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

    def sync_project(self, dataset_list):
        """ Logical separation of sync project

        Args:
            dataset_list: The page with UI elements

        """
        # Click on Sync button
        is_clicked = dataset_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Check for the publish all workflow window appear or not
        is_verified = dataset_list.project_menu_component.check_publish_all_workflow_appear()
        assert is_verified, "Publish all workflow window should not appear"

        # Click on the continue button
        is_clicked = dataset_list.project_menu_component.click_continue_button()
        assert is_clicked, "Could not click on the continue button"

        # Enable private mode for project
        is_enabled = dataset_list.project_menu_component.enable_private_mode_for_all()
        assert is_enabled, "Could not enable private mode for project"

        # Click on publish button on publish window
        is_clicked = dataset_list.project_menu_component.click_publish_all_and_sync_button()
        assert is_clicked, "Could not click project publish button on project publish window"

        # Check publish all window is closed or not
        is_verified = dataset_list.project_menu_component.check_publish_all_window_closed()
        assert is_verified, "Publish all window is not closed"

        # Check private lock icon presence
        is_checked = dataset_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = dataset_list.container_status_component.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = dataset_list.container_status_component.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def verify_dataset_auto_imported(self, project_list, dataset_title):
        """ Logical separation of verify dataset auto imported

        Args:
            project_list: The page with UI elements
            dataset_title: Title of the dataset

        """
        # Click on Input Data tab
        is_clicked = project_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click on Input Data tab"

        # Verify dataset is present
        is_clicked = project_list.code_input_output_component.verify_dataset_is_present(dataset_title)
        assert is_clicked, "Could not verify dataset in Input Data tab"

        # Click dataset name on Input Data tab
        is_clicked = project_list.code_input_output_component.click_dataset_name(dataset_title)
        assert is_clicked, "Could not click dataset name on Input Data tab"

        # Get dataset title
        dataset_title = project_list.project_menu_component.get_title()
        assert dataset_title == dataset_title, "Could not get the dataset title"
