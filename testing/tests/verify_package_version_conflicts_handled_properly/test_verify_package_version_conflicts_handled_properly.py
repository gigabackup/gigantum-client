"""Test call for verify package version conflicts are handled properly"""
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


@pytest.mark.verifyPackageVersionConflictsHandledProperly
class TestVerifyPackageVersionConflictsHandledProperly:
    """Includes test methods for verify package version conflicts handled properly"""

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
    def test_verify_package_version_conflicts_handled_properly(self, clean_up_project, server_data_fixture,
                                                               clean_up_remote_project):
        """Test method to verify package version conflicts are handled properly"""
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

        # Package gtmunit1
        package = namedtuple('package', ('name', 'version'))
        package_gtmunit1 = package("gtmunit1", "0.12.4")

        # Add package 'gtmunit1'
        self.add_package(package_list, package_gtmunit1)

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

        # Change package details
        package_gtmunit1 = package("gtmunit1", "0.2.4")

        # Change package
        self.change_package_version(package_list, package_gtmunit1)

        # Click sync button
        self.click_sync_button(package_list)

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Select project
        is_clicked = package_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Change package details
        package_gtmunit1 = package("gtmunit1", "0.2.0")

        # Change package
        self.change_package_version(package_list, package_gtmunit1)

        commands = namedtuple('command', ('command_text', 'output', 'error_message'))
        command_text = ['pip freeze | grep gtmunit']
        output = ['gtmunit1==0.2.0']
        error_message = 'Verification of package failed'
        gtmunit_grep_command = commands(command_text, output, error_message)
        verification_message = ProjectUtility().verify_command_execution(self.driver, [gtmunit_grep_command])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Resolve conflict theirs
        self.resolve_conflict_theirs(package_list)

        # DMK: temporary fix due to issue with package merge conflicts that will
        # be resolved in: https://github.com/gigantum/gigantum-client/issues/1804
        self.driver.refresh()

        # Verify their package (0.2.4) is present
        package_gtmunit1 = package("gtmunit1", "0.2.4")
        is_verified = package_list.verify_package_listing([package_gtmunit1])
        assert is_verified, "Could not verify package 'gtmunit1'"

        # DMK: This code is commented out until fix in: https://github.com/gigantum/gigantum-client/issues/1804
        # Open Jupyter_lab and verify packages
        # commands = namedtuple('command', ('command_text', 'output', 'error_message'))
        # command_text = ['pip freeze | grep gtmunit']
        # output = ['gtmunit1==0.2.4']
        # error_message = 'Verification of package failed'
        # gtmunit_grep_command = commands(command_text, output, error_message)
        # verification_message = ProjectUtility().verify_command_execution(self.driver, [gtmunit_grep_command])
        # assert verification_message == ProjectConstants.SUCCESS.value, verification_message

    def add_package(self, package_list, package_gtmunit1):
        """Logical separation of add package

        Args:
            package_list: The page with UI elements
            package_gtmunit1: Package details include name and it's version

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
        is_package_title_typed = package_list.type_package_name("gtmunit1")
        assert is_package_title_typed, "Could not type package title"

        # Click on Add button
        is_clicked = package_list.click_add()
        assert is_clicked, "Could not click Add button"

        # Monitor package list status
        is_status_changed = package_list.monitor_package_list_status("1 added", 60)
        assert is_status_changed, "Could not get the package added status"

        # Verify package and it's version
        is_verified = package_list.verify_packages(package_gtmunit1)
        assert is_verified, "Could not verify package and version"

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

        # Verify package 'gtmunit1' and it's version
        is_verified = package_list.verify_package_listing([package_gtmunit1])
        assert is_verified, "Could not verify package 'gtmunit1'"

    def change_package_version(self, package_list, package_gtmunit1):
        """Logical separation of change package

        Args:
            package_list: The page with UI elements
            package_gtmunit1: Package details include name and it's version

        """
        # Click on Environment Tab
        is_clicked = package_list.click_environment_tab()
        assert is_clicked, "Could not click Environment tab"

        # Click on Add Package button
        is_clicked = package_list.click_add_package()
        assert is_clicked, "Could not click Add Package"

        # Input package name and version
        is_package_title_version_typed = package_list.type_package_name_and_version(package_gtmunit1.name,
                                                                                    package_gtmunit1.version)
        assert is_package_title_version_typed, "Could not type package title and it's version"

        # Click on Add button
        is_clicked = package_list.click_add()
        assert is_clicked, "Could not click Add button"

        # Monitor package list status
        is_status_changed = package_list.monitor_package_list_status("1 added", 60)
        assert is_status_changed, "Could not get the package added status"

        # Verify package and it's version
        is_verified = package_list.verify_packages(package_gtmunit1)
        assert is_verified, "Could not verify package and version"

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

        # Verify package 'gtmunit1' and it's version
        is_verified = package_list.verify_package_listing([package_gtmunit1])
        assert is_verified, "Could not verify package 'gtmunit1'"

    def click_sync_button(self, package_list):
        """Logical separation of click sync button

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

    def resolve_conflict_theirs(self, package_list):
        """Logical separation of resolve conflict theirs

        Args:
            package_list: The page with UI elements

        """
        is_clicked = package_list.project_menu_component.click_sync_button()
        assert is_clicked, "Could not click Sync button"

        # Monitor container status to go through Stopped -> Syncing
        is_status_changed = package_list.monitor_container_status("Syncing", 60)
        assert is_status_changed, "Could not get Syncing status"

        # Check sync conflict modal appears
        is_checked = package_list.project_sync_conflict_modal_component.check_sync_conflict_modal_presence()
        assert is_checked, "Could not get sync conflict modal presence"

        # Click Use theirs button in sync conflict modal
        is_clicked = package_list.project_sync_conflict_modal_component.click_use_theirs_button()
        assert is_clicked, "Could not click Use theirs button in sync conflict modal"

        # Check sync conflict modal closed
        is_checked = package_list.project_sync_conflict_modal_component.check_sync_conflict_modal_absence()
        assert is_checked, "Could not close sync conflict modal"

        # Check for the presence of Sync complete pop up message
        is_checked = package_list.project_menu_component.check_sync_complete_pop_up_presence()
        assert is_checked, "Could not get Sync complete pop up window"

        # Monitor container status -> Stopped (this package installs really fast, so you miss the
        # building step on most reasonably fast compute resources)
        time.sleep(3)
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"
