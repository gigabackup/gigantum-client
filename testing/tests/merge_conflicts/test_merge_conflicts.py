"""Test call for verify merge conflicts"""
import pytest
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project
from tests.test_fixtures import clean_up_remote_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
import time
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.mergeConflicts
class TestMergeConflicts:
    """Includes test methods for basic project, publish and verify merge conflicts"""

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
    def test_add_project_publish_verify_merge_conflicts(self, clean_up_project, clean_up_remote_project,
                                                        server_data_fixture):
        """Test method to create a project, publish and verify merge conflicts"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Set project details into remote project clean up fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone('user1:created')
        assert is_dropped, "Could not drag and drop text file in to code data drop zone"

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Publish project
        self.publish_project(project_list, user2_credentials)

        # Switch user1 to user2
        self.switch_user(project_list, user2_credentials, server_data_fixture)

        # Import project
        self.import_project(project_list, project_title)

        # Update files and sync
        self.update_files_and_sync(project_list, project_title)

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch user2 to user1
        self.switch_user(project_list, user1_credentials, server_data_fixture)

        # Update files and sync -> Conflict, Abort
        self.update_files_and_sync_conflict_abort(project_list, project_title)

        # Resolve conflict -> Theirs
        self.resolve_conflict_theirs(project_list, project_title)

        # Create another conflict
        self.create_another_conflict(project_list, project_title)

        # Switch user1 to user2
        self.switch_user(project_list, user2_credentials, server_data_fixture)

        # Update files and sync -> Conflict, Mine
        self.update_files_and_sync_conflict_mine(project_list, project_title)

        # Switch user2 to user1
        self.switch_user(project_list, user1_credentials, server_data_fixture)

        # Sync and verify resolution
        self.sync_and_verify_resolution(project_list, project_title)

    def switch_user(self, project_list,  user_credentials, server_details):
        """Logical separation of switch user in gigantum client

        Args:
            project_list: The page with UI elements
            user_credentials: Includes username and password
            server_details: Details of the current server

        """
        # Click on profile menu
        is_clicked = project_list.project_listing_component.profile_menu_click()
        assert is_clicked, "Could not click profile menu button"

        # Click on logout button
        is_clicked = project_list.project_listing_component.log_out()
        assert is_clicked, "Could not click logout button"

        # Load Landing Page
        landing_page = LandingPage(self.driver, False)

        # Click server button
        landing_page.landing_component.click_server(server_details.server_name)

        # Load Login page
        login_page = LoginFactory().load_login_page(server_details.login_type, self.driver)

        # Load Project Listing page
        project_list = login_page.login(user_credentials.user_name, user_credentials.password)
        assert project_list.project_listing_component.get_project_title() == "Projects"

    def publish_project(self, project_list, user2_credentials):
        """Logical separation of publish project functionality

        Args:
            project_list: The page with UI elements
            user2_credentials: username of the collaborator

        """
        # Click on project publish button
        is_clicked = project_list.project_menu_component.click_publish_button()
        assert is_clicked, "Could not click project publish button"

        # Enable private mode in project publish window
        is_enabled = project_list.project_menu_component.enable_private_mode()
        assert is_enabled, "Could not enable private mode in project publish window"

        # Click on publish button on publish window
        is_clicked = project_list.project_menu_component.click_publish_window_button()
        assert is_clicked, "Could not click project publish button on project publish window"

        # Monitor container status to go through Stopped -> Publishing
        is_status_changed = project_list.monitor_container_status("Publishing", 60)
        assert is_status_changed, "Could not get Publishing status"

        # Monitor container status to go through Publishing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Check private lock icon presence
        is_checked = project_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Click on Collaborators button
        is_clicked = project_list.project_menu_component.click_collaborators_button()
        assert is_clicked, "Could not click Collaborators button"

        # Input collaborator name into input area
        is_typed = project_list.collaborators_modal_component.add_collaborator(user2_credentials.display_name)
        assert is_typed, "Could not type collaborator into input area"

        # Select Admin permission for collaborator
        is_selected = project_list.collaborators_modal_component.select_admin_permission()
        assert is_selected, "Could not select Admin permission from drop down"

        # Click on add collaborator button
        is_clicked = project_list.collaborators_modal_component.click_add_collaborator_button()
        assert is_clicked, "Could not click on add collaborators button"

        # Verify collaborator is listed
        is_verified = project_list.collaborators_modal_component.verify_collaborator_is_listed(
            user2_credentials.display_name)
        assert is_verified, "Collaborator is not listed in the modal"

        # Click on collaborator modal close button
        is_clicked = project_list.collaborators_modal_component.click_collaborator_modal_close()
        assert is_clicked, "Could not close collaborator modal"

    def import_project(self, project_list, project_title):
        """ Import project from server

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
        is_clicked = project_list.server_component.click_project_import_button(project_title)
        assert is_clicked, "Could not click import button in server page"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = project_list.monitor_container_status("Building", 5)
        if not is_status_changed:
            # DMK Note: In some cases the build finishes so fast it is at the Stopped state already.
            # This extra case verifies that it is indeed Stopped and not bouncing.
            is_stopped = project_list.monitor_container_status("Stopped", 1)
            if is_stopped:
                time.sleep(2)
                is_stopped = project_list.monitor_container_status("Stopped", 1)
                assert is_stopped, "Could not get Building status and verify container was already ready"
            else:
                assert is_stopped, "Could not get Building status and verify container was already ready"
        else:
            assert is_status_changed, "Could not get Building status"

        # Monitor container status to go through Building -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def update_files_and_sync(self, project_list, project_title):
        """ Performs file content update and sync

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        """
        # Verify file content in Code directory
        is_collaborator = True
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user1:created', project_title, is_collaborator)
        assert is_verified, "Could not verify the file contents in Code directory"

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser(
            'user2:modified1')
        assert is_dropped, "Could not drag and drop text file in to code data file browser"

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

    def update_files_and_sync_conflict_abort(self, project_list, project_title):
        """ Update file contents and sync -> Conflict, Abort

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        """
        # Select current project
        is_selected = project_list.project_listing_component.click_project(project_title)
        assert is_selected, "Could not select project from project listing"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user1:created', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser(
            'user1:modified1')
        assert is_dropped, "Could not drag and drop text file in to code data file browser"

        # Click on Sync button
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal appears
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert is_checked, "Could not get sync conflict modal presence"

        # Click Abort button in sync conflict modal
        is_clicked = project_list.project_sync_conflict_modal_component.click_abort_button()
        assert is_clicked, "Could not click Abort button in sync conflict modal"

        # Check sync conflict modal closed
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_absence()
        assert is_checked, "Could not close sync conflict modal"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user1:modified1', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"

    def resolve_conflict_theirs(self, project_list, project_title):
        """ Resolve conflict theirs

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        Returns:

        """
        # Click on Sync button
        # DMK NOTE: Don't know why yet, but you can't click the sync button after the conflict modal closes
        self.driver.refresh()
        time.sleep(3)
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal appears
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert is_checked, "Could not get sync conflict modal presence"

        # Click Use theirs button in sync conflict modal
        is_clicked = project_list.project_sync_conflict_modal_component.click_use_theirs_button()
        assert is_clicked, "Could not click Use theirs button in sync conflict modal"

        # Check sync conflict modal closed
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_absence()
        assert is_checked, "Could not close sync conflict modal"

        # Check for the presence of Sync complete pop up message
        is_checked = project_list.project_menu_component.check_sync_complete_pop_up_presence()
        assert is_checked, "Could not get Sync complete pop up window"

        # Monitor container status to go through Stopped -> Building
        project_list.monitor_container_status("Building", 10)

        # Monitor container status -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user2:modified1', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"

    def create_another_conflict(self, project_list, project_title):
        """ Create another conflict

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        Returns:

        """
        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser(
            'user1:modified2')
        assert is_dropped, "Could not drag and drop text file in to code data file browser"

        # Click on Sync button
        # DMK NOTE: Don't know why yet, but you can't click the sync button after the conflict modal closes
        self.driver.refresh()
        time.sleep(3)
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal is not appears
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert not is_checked, "Sync conflict modal appears"

        # Monitor container status to go through Stopped -> Building
        project_list.monitor_container_status("Building", 10)

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def update_files_and_sync_conflict_mine(self, project_list, project_title):
        """ Update file contents and sync -> Conflict, Mine

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        """
        # Select current project
        is_selected = project_list.project_listing_component.click_project(project_title)
        assert is_selected, "Could not select project from project listing"

        # Verify file content in Code directory
        is_collaborator = True
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user2:modified1', project_title,
                                                                 is_collaborator)
        assert is_verified, "Could not verify the file contents in Code directory"

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data file browser
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser(
            'user2:modified2')
        assert is_dropped, "Could not drag and drop text file in to code data file browser"

        # Click on Sync button
        # DMK NOTE: Don't know why yet, but you can't click the sync button after the conflict modal closes
        self.driver.refresh()
        time.sleep(3)
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal appears
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert is_checked, "Sync conflict modal not appears"

        # Click Mine button in sync conflict modal
        is_clicked = project_list.project_sync_conflict_modal_component.click_mine_button()
        assert is_clicked, "Could not click Mine button in sync conflict modal"

        # Check sync conflict modal closed
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_absence()
        assert is_checked, "Could not close sync conflict modal"

        # Check for the presence of Sync complete pop up message
        is_checked = project_list.project_menu_component.check_sync_complete_pop_up_presence()
        assert is_checked, "Could not get Sync complete pop up window"

        # Monitor container status to go through Stopped -> Building
        project_list.monitor_container_status("Building", 10)

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user2:modified2', project_title,
                                                                 is_collaborator)
        assert is_verified, "Could not verify the file contents in Code directory"

    def sync_and_verify_resolution(self, project_list, project_title):
        """ Sync and verify resolution

        Args:
            project_list: The page with UI elements
            project_title: Title of the current project

        """
        # Select current project
        is_selected = project_list.project_listing_component.click_project(project_title)
        assert is_selected, "Could not select project from project listing"

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user1:modified2', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"

        # TODO: Sync button click action is not successful even though it is found clickable.
        #  Possible only by providing a sleep.Need to check this out.
        time.sleep(5)

        # Click on Sync button
        is_clicked = project_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = project_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal is not appears
        is_checked = project_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert not is_checked, "Sync conflict modal appears"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Monitor container status to go through Stopped -> Building
        project_list.monitor_container_status("Building", 10)

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Verify file content in Code directory
        is_verified = ProjectHelperUtility().verify_file_content('code', 'user2:modified2', project_title)
        assert is_verified, "Could not verify the file contents in Code directory"
