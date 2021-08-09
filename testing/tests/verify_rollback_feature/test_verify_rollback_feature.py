"""Test call for verify rollback feature"""
from collections import namedtuple
import pytest
from client_app.pages.package_listing.package_listing_page import PackageListingPage
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.verifyRollbackFeature
class TestVerifyRollbackFeature:
    """Includes test methods for verify rollback feature"""

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
    def test_verify_rollback_feature(self, clean_up_project, server_data_fixture):
        """Test method to verify rollback feature"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Package Page
        package_list = PackageListingPage(self.driver)
        assert package_list is not None, "Could not load Project Listing Page"

        # Click on Code Tab
        is_clicked = package_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data drop zone
        is_dropped = package_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone('rollback:point')
        assert is_dropped, "Could not drag and drop text file in to code data drop zone"

        # Add package 'requests'
        self.add_package(package_list)

        # Rollback last activity
        self.rollback(package_list)

    def add_package(self, package_list):
        """Logical separation of add package

        Args:
            package_list: The page with UI elements

        """
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
        is_package_title_typed = package_list.type_package_name("requests")
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

    def rollback(self, package_list):
        """Logical separation of rollback

        Args:
            package_list: The page with UI elements

        """
        # Click 'Activity' tab
        is_clicked = package_list.project_activity_component.click_activity_tab()
        assert is_clicked, "Could not click Activity tab"

        # Verify activity feed 'Added 1 pip package(s).'
        is_verified = package_list.project_activity_component.verify_activity_feed("Added 1 pip package(s).")
        assert is_verified, "Could not verify activity feed 'Added 1 pip package(s).'"

        # Verify activity feed 'Uploaded 1 new file(s)'
        is_verified = package_list.project_activity_component.verify_activity_feed("Uploaded 1 new file(s)")
        assert is_verified, "Could not verify activity feed 'Uploaded 1 new file(s)'"

        # Move to rollback element
        is_moved = package_list.project_activity_component.move_to_rollback_button_and_click("Uploaded 1 new file(s)")
        assert is_moved, "Could not move to rollback element"

        # Verify create branch window is opened
        is_verified = package_list.project_activity_component.verify_create_rollback_branch_window_opened()
        assert is_verified, "Create rollback branch window is not opened"

        # Click create rollback branch button
        is_clicked = package_list.project_activity_component.click_create_rollback_branch_button()
        assert is_clicked, "Could not click create rollback branch button"

        # Verify create branch window is closed
        is_verified = package_list.project_activity_component.verify_create_rollback_branch_window_closed()
        assert is_verified, "Create rollback branch window is not closed"

        # Monitor container status to go through building -> stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 40)
        assert is_status_changed, "Could not get Stopped status"

        # Verify activity feed 'Added 1 pip package(s).' is not present
        is_verified = package_list.project_activity_component.verify_activity_feed("Added 1 pip package(s).")
        assert not is_verified, "Activity feed 'Added 1 pip package(s).' is still present"

        # Verify activity feed 'Uploaded 1 new file(s)'
        is_verified = package_list.project_activity_component.verify_activity_feed("Uploaded 1 new file(s)")
        assert is_verified, "Could not verify activity feed 'Uploaded 1 new file(s)'"
