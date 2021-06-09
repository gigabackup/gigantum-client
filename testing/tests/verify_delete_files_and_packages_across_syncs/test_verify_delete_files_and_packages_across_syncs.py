"""Test call for verify delete files and packages across syncs"""
from collections import namedtuple
import pytest
from client_app.pages.package_listing.package_listing_page import PackageListingPage
from tests.helper.dataset_utility import DatasetUtility
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project, clean_up_remote_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
import time
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.verifyDeleteFilePackageAcrossSync
class TestVerifyDeleteFilesAndPackagesAcrossSyncs:
    """Includes test methods for verify delete files and packages across syncs"""

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
    def test_verify_delete_files_and_packages_across_syncs(self, clean_up_project, server_data_fixture,
                                                           clean_up_remote_project):
        """Test method to verify delete files and packages across syncs"""
        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Instance of ProjectUtility class
        project_utility = ProjectUtility()

        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Package Page
        package_list = PackageListingPage(self.driver)
        assert package_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = package_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Set project details into 'clean_up_remote_project' fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Add file 'requirements.txt' and package 'gtmunit1'
        self.add_file_and_package(package_list)

        # Verify gtmunit1 package in jupyter_lab
        commands = namedtuple('command', ('command_text', 'output', 'error_message'))
        gtmunit_grep_command = commands(['pip freeze | grep gtmunit'], ['gtmunit1==0.12.4'],
                                        'Verification of package gtmunit1 failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [gtmunit_grep_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Publish project
        is_success_msg = ProjectUtility().publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Add user2 as collaborator
        is_success_msg = dataset_utility.add_collaborator(self.driver, user2_credentials.display_name, 'Admin')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Import Project
        is_success_msg = project_utility.import_project(self.driver, project_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete file and package
        self.delete_file_and_package(package_list)

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Select project
        is_clicked = package_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Click on Code Tab
        is_clicked = package_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Verify file is present
        is_verified = package_list.code_input_output_component.verify_file_is_present('requirements.txt')
        assert is_verified, "Could not verify the file is present or not"

        # Verify gtmunit1 package in jupyter_lab
        verification_message = ProjectUtility().verify_command_execution(self.driver, [gtmunit_grep_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Sync and verify file and package
        self.sync_and_verify(package_list)

        # Verify gtmunit1 package in jupyter_lab
        gtmunit_grep_command = commands(['pip freeze | grep gtmunit'], [],
                                        'Verification of package gtmunit1 failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [gtmunit_grep_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

    def add_file_and_package(self, package_list):
        """Logical separation of add file and package

        Args:
            package_list: The page with UI elements

        """
        # Click on Code Tab
        is_clicked = package_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data drop zone
        is_dropped = package_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone('user1:created')
        assert is_dropped, "Could not drag and drop text file in to code data drop zone"

        # Click on Environment Tab
        is_clicked = package_list.click_environment_button()
        assert is_clicked, "Could not click Environment tab"

        # Get package body text
        package_body_text = package_list.get_package_body_text()
        assert package_body_text == "No packages have been added to this project", "Package body text incorrect"

        # Click on Add Package button
        is_clicked = package_list.click_add_package()
        assert is_clicked, "Could not click Add Package"

        # Input package name
        is_package_title_typed = package_list.type_package_name("gtmunit1")
        assert is_package_title_typed, "Could not type package title"

        # Click on Add button
        is_clicked = package_list.click_add()
        assert is_clicked, "Could not click Add button"

        # Monitor package list status
        is_status_changed = package_list.monitor_package_list_status("1 added", 60)
        assert is_status_changed, "Could not get the package added status"

        # Click on Install all button
        is_clicked = package_list.click_install_all_packages()
        assert is_clicked, "Could not click Install all"

        # Monitor appearance of build modal window
        is_found = package_list.monitor_build_modal(60)
        assert is_found, "Could not found the build model"

        # Monitor closing of build model window
        is_closed = package_list.check_build_modal_closed(60)
        assert is_closed, "Could not close the build modal"

        # Monitor container status to go through building -> stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def delete_file_and_package(self, package_list):
        """Logical separation of add file and package

        Args:
            package_list: The page with UI elements

        """
        # Click on Code Tab
        is_clicked = package_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Click file delete button
        is_clicked = package_list.code_input_output_component.click_file_delete('requirements.txt')
        assert is_clicked, "Could not delete file"

        # Click on Environment Tab
        is_clicked = package_list.click_environment_tab()
        assert is_clicked, "Could not click Environment tab"

        # Remove a package
        is_removed = package_list.delete_package('gtmunit1')
        assert is_removed, "Could not remove package"

        # Monitor container status to go through building -> stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Click on Sync button
        is_clicked = package_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = package_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def sync_and_verify(self, package_list):
        """Logical separation of add file and package

        Args:
            package_list: The page with UI elements

        """
        # Click on Sync button
        is_clicked = package_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = package_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = package_list.monitor_container_status("Building", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Monitor container status to go through Syncing -> Stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Verify file is not present
        is_verified = package_list.code_input_output_component.verify_file_is_present('requirements')
        assert not is_verified, "Could not verify the file is present or not"
