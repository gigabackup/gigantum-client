"""Test call for Add sensitive file"""
import time
import pytest
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.package_listing.package_listing_page import PackageListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from collections import namedtuple
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from tests.test_fixtures import clean_up_remote_project


@pytest.mark.addSensitiveFile
class TestAddPackageUsingDockerSnippets:
    """Includes test methods for add, remove, and update a sensitive file"""

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
    def test_add_sensitive_file(self, clean_up_project, clean_up_remote_project):
        """Test method to add, remove, and update a sensitive file"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Set project details into 'clean_up_remote_project' fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Load Project Package Page
        package_list = PackageListingPage(self.driver)
        assert package_list is not None, "Could not load Project Listing Page"

        # Add sensitive file
        self.add_sensitive_file(package_list)

        # Open Jupyter_lab and verify packages and environment variable
        commands = namedtuple('command', ('command_text', 'output', 'error_message'))

        file_command = commands(['! cat ~/keys/token.txt'], ['my-fake-token'], 'Verification of file failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [file_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Edit sensitive file
        self.edit_sensitive_file(package_list)

        file_command = commands(['! cat ~/keys/token.txt'], ['my-updated-token'], 'Verification of file failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [file_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Scroll to window top
        package_list.scroll_to_page_top()

        # Publish project
        project_utility = ProjectUtility()
        is_success_msg = project_utility.publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete local project
        is_success_msg = project_utility.delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Import project
        self.import_project(project_list, project_title)

        # Verify re-add sensitive file
        self.verify_re_add_sensitive_file(package_list)

        file_command = commands(['! cat ~/keys/token.txt'], ['my-different-token'], 'Verification of file failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [file_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Verify sensitive file delete
        self.verify_sensitive_file_delete(package_list)
        time.sleep(1)

        file_command = commands(['! cat ~/keys/token.txt'],
                                ['cat: /home/giguser/keys/token.txt: No such file or directory'],
                                'Verification of file failed')
        verification_message = ProjectUtility().verify_command_execution(self.driver, [file_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

    def add_sensitive_file(self, package_list):
        """ Add sensitive file

        Args:
            package_list: The page with UI elements
        """
        # Click on Environment Tab
        is_clicked = package_list.click_environment_button()
        assert is_clicked, "Could not click Environment tab"

        # Scroll window to bottom
        is_scrolled = package_list.scroll_window_to_bottom()
        assert is_scrolled, "Could not scrolled the window to bottom"

        # Click on Advanced configuration settings button
        is_clicked = package_list.click_advanced_configuration_settings()
        assert is_clicked, "Could not click advanced configuration settings"

        # Scroll to advanced configuration element
        is_clicked = package_list.scroll_to_advanced_configuration()
        assert is_clicked, "Could not scroll to element"

        # Input sensitive file
        is_added = package_list.input_sensitive_file('token.txt', 'my-fake-token')
        assert is_added, "Could not add sensitive file"

        # Input destination directory
        is_added = package_list.add_destination_directory('keys')
        assert is_added, "Could not add destination directory"

        # Click sensitive file save button
        is_clicked = package_list.click_sensitive_file_save_button()
        assert is_clicked, "Could not click sensitive file save button"

        # Verify sensitive file is added
        is_verified = package_list.verify_sensitive_file_is_added('token.txt')
        assert is_verified, "Sensitive file is not added"

    def edit_sensitive_file(self, package_list):
        """ Edit sensitive file

        Args:
            package_list: The page with UI elements
        """
        # Scroll to advanced configuration element
        is_clicked = package_list.scroll_to_advanced_configuration()
        assert is_clicked, "Could not scroll to element"

        # Click edit sensitive file button
        is_clicked = package_list.click_edit_sensitive_file_button()
        assert is_clicked, "Could not click on edit sensitive file button"

        # Replace sensitive file
        is_clicked = package_list.replace_sensitive_file('token.txt', 'my-updated-token')
        assert is_clicked, "Could not replace sensitive file"

        # Verify sensitive file is added
        is_verified = package_list.verify_sensitive_file_is_added('token.txt')
        assert is_verified, "Sensitive file is not added"

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
        is_clicked = project_list.server_component.click_import_button(project_title)
        assert is_clicked, "Could not click import button in server page"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = project_list.monitor_container_status("Building", 60)
        assert is_status_changed, "Could not get Building status"

        # Monitor container status to go through Building -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

    def verify_re_add_sensitive_file(self, package_list):
        """ Verify re-add sensitive file

        Args:
            package_list: The page with UI elements
        """
        # Click on Environment Tab
        is_clicked = package_list.click_environment_tab()
        assert is_clicked, "Could not click Environment tab"

        # Scroll window to bottom
        is_scrolled = package_list.scroll_window_to_bottom()
        assert is_scrolled, "Could not scrolled the window to bottom"

        # Verify sensitive file is missing
        time.sleep(1)
        is_verified = package_list.verify_sensitive_file_is_missing()
        assert is_verified, "Could not verify the sensitive file"

        # Replace sensitive file
        is_clicked = package_list.replace_sensitive_file('token.txt', 'my-different-token')
        assert is_clicked, "Could not replace sensitive file"

        # Verify sensitive file is added
        is_verified = package_list.verify_sensitive_file_is_added('token.txt')
        assert is_verified, "Sensitive file is not added"

    def verify_sensitive_file_delete(self, package_list):
        """ Verify sensitive file delete

        Args:
            package_list: The page with UI elements
        """
        # Scroll to advanced configuration element
        is_clicked = package_list.scroll_to_advanced_configuration()
        assert is_clicked, "Could not scroll to element"

        # Click sensitive file delete button
        is_clicked = package_list.click_sensitive_file_delete_button()
        assert is_clicked, "Could not click on sensitive file delete button"

        # Click sensitive file delete yes button
        is_clicked = package_list.click_sensitive_file_delete_yes_button()
        assert is_clicked, "Could not click on sensitive file delete button"
