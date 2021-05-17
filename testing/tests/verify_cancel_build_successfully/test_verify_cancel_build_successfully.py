"""Test call for verifying package build cancel successfully"""
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


@pytest.mark.verifyCancelBuildSuccessfully
class TestVerifyBuildCancelSuccessfully:
    """Includes test methods for basic project creation and verifying package build cancel successfully"""

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
    def test_verify_package_with_broken_build(self, clean_up_project):
        """Test method to verifying package build cancel successfully"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Package Page
        package_list = PackageListingPage(self.driver)
        assert package_list is not None, "Could not load Project Listing Page"

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
        is_package_title_typed = package_list.type_package_name("tensorflow")
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

        # Click on cancel build button
        is_clicked = package_list.click_cancel_build_button()
        assert is_clicked, "Could not click cancel build button"

        # Check whether the build is failed or not
        is_clicked = package_list.check_build_failed()
        assert is_clicked, "Build is not failed"

        # Click on clear cache and build button
        is_clicked = package_list.click_clear_cache_and_build_button()
        assert is_clicked, "Could not click clear cache and build button"

        # Monitor closing of build model window
        is_closed = package_list.check_build_modal_closed(60)
        assert is_closed, "Could not close the build modal"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = package_list.monitor_container_status("Building", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Click on container status button to stop the build
        is_clicked = package_list.container_status_component.click_container_status()
        assert is_clicked, "Could not click container status"

        # Monitor container status to go through running -> stopped
        package_list.move_to_element()

        # Monitor container status to go through Building -> Stopped
        is_status_changed = package_list.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Check for rebuild required
        is_checked = package_list.check_rebuild_required()
        assert is_checked, "Could not check rebuild required"



