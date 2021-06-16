"""Test call for publish project from collaborator modal"""
import pytest
import time
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.helper.project_utility import ProjectUtility
from tests.test_fixtures import clean_up_project
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture
from tests.test_fixtures import clean_up_remote_project


@pytest.mark.publishFromCollaboratorModal
class TestPublishFromCollaboratorModal:
    """Includes test methods for basic project creation, and publish from collaborator modal"""

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
    def test_publish_project_from_collaborator_modal(self, clean_up_project, clean_up_remote_project):
        """Test method to publish project from collaborator modal."""
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

        # Publish project
        self.publish_project(project_list)

    def publish_project(self, project_list):
        """Logical separation of publish project functionality

        Args:
            project_list: The page with UI elements

        """

        # Click on Collaborators button
        is_clicked = project_list.project_menu_component.click_collaborators_button()
        time.sleep(.5)
        assert is_clicked, "Could not click Collaborators button"

        # Click publish button on collaborator modal
        is_clicked = project_list.collaborators_modal_component.click_collaborator_publish_button()
        assert is_clicked, "Could not click publish button on collaborator modal"

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
