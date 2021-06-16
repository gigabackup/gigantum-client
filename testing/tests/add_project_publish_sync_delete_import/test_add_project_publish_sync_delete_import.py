"""Test call for Add Project, Publish, Sync, Delete and Import"""
import pytest
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
import time
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.addProjectPublishSyncDeleteImport
class TestAddProjectPublishSyncDeleteImport:
    """Includes test methods for basic project, publish, sync, delete and import"""

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
    def test_add_project_publish_sync_delete_import(self, clean_up_project):
        """Test method to create a project, publish, sync, delete and import"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Add files into code data, input data and output data
        self.add_files(project_list, project_title)

        # Publish project
        is_success_msg = ProjectUtility().publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Update files and sync
        self.update_files_and_sync(project_list)

        # Delete local project
        is_success_msg = ProjectUtility().delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify project is not listed in project listing page
        is_verified = project_list.project_listing_component.verify_project_in_project_listing(project_title)
        assert is_verified, "Project is exist in the project listing page"

        # Verify project no longer exists on disk
        is_verified = ProjectHelperUtility().check_project_removed_from_disk(project_title)
        assert is_verified, "Project is exist in the disk"

        # Verify project image is no longer exist
        is_verified = ProjectHelperUtility().check_project_image_is_removed(project_title)
        assert is_verified, "Project image is not removed"

        # Import project and verify project contents
        self.import_project_and_verify_project_content(project_list, project_title)

        # Delete local project
        is_success_msg = ProjectUtility().delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete project from server
        is_success_msg = ProjectUtility().delete_project_from_server(self.driver, project_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

    def add_files(self, project_list, project_title):
        """Logical separation of add files in to code data, input data and output data

        Args:
            project_list: The page with UI elements
            project_title: Title of the project

        """
        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in to code data drop zone"

        # Drag and drop text file into code data untracked folder
        is_dropped = ProjectHelperUtility().move_file_to_untracked_folder('code', project_title)
        assert is_dropped, "Could not drag and drop text file into code data untracked folder"

        # Drag and drop text file into code data file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser('created')
        assert is_dropped, "Could not drag and drop text file in to code data file browser"

        # Click on Input Data tab
        is_clicked = project_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click Input Data tab"

        # Drag and drop text file into input drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_input_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in input drop zone"

        # Drag and drop text file into input untracked folder
        is_dropped = ProjectHelperUtility().move_file_to_untracked_folder('input', project_title)
        assert is_dropped, "Could not drag and drop text file into input untracked folder"

        # Drag and drop text file into input file browser area
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_input_file_browser('created')
        assert is_dropped, "Could not drag and drop text file in to input file browser area"

        # Click on Output Data tab
        is_clicked = project_list.project_menu_component.click_output_data_tab()
        assert is_clicked, "Could not click Output Data tab"

        # Drag and drop text file into output drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_output_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in output drop zone"

        # Drag and drop text file into output untracked folder
        is_dropped = ProjectHelperUtility().move_file_to_untracked_folder('output', project_title)
        assert is_dropped, "Could not drag and drop text file into output untracked folder"

        # Drag and drop text file into output file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_output_file_browser('created')
        assert is_dropped, "Could not drag and drop text file in to output file browser"

    def update_files_and_sync(self, project_list):
        """Logical separation of updates files and sync

        Args:
            project_list: The page with UI elements

        """
        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data file browser area
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser('updated')
        assert is_dropped, "Could not drag and drop text file in to code file browser area"

        # Click on Input Data tab
        is_clicked = project_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into input data file browser area
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_input_file_browser('updated')
        assert is_dropped, "Could not drag and drop text file in to input data file browser area"

        # Click on Sync button
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Monitor container status to go through Stopped -> Building
        project_list.monitor_container_status("Building", 10)

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def import_project_and_verify_project_content(self, project_list, project_title):
        """ Logical separation of import project and verify project content

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        """
        # Click server tab
        is_clicked = project_list.server_component.click_server_tab()
        assert is_clicked, "Could not click server tab"

        # Verify project in server page
        is_verified = project_list.server_component.verify_title_in_server(project_title)
        assert is_verified, "Could not verify project in server"

        # Click import button in server page
        is_clicked = project_list.server_component.click_import_button(project_title)
        assert is_clicked, "Could not click import button in server page"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = project_list.monitor_container_status("Building", 60)
        assert is_status_changed, "Could not get Building status"

        # Monitor container status to go through Building -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Verify the untracked directories in code, input, and output are all empty
        is_verified = ProjectHelperUtility().verify_untracked_directory_is_empty(project_title)
        assert is_verified, "Untracked directories in code, input and output are not empty"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'updated', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"

        # Verify file content in Input data directory
        is_verified = ProjectHelperUtility().verify_file_content('input', 'updated', project_title)
        assert is_verified, "Could not verify the file contents in Input data directory"

        # Verify file content in Output data directory
        is_verified = ProjectHelperUtility().verify_file_content('output', 'created', project_title)
        assert is_verified, "Could not verify the file contents in Output data directory"
