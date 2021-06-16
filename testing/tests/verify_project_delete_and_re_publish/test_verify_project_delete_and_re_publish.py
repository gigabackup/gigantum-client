"""Test call for verify project delete and re-publish works"""
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


@pytest.mark.verifyProjectDeleteAndRepublish
class TestVerifyProjectDeleteAndRepublish:
    """Includes test methods for verify project delete and re-publish works"""

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
    def test_project_delete_and_re_publish(self, clean_up_project):
        """Test method to verify project delete and re-publish works"""
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
        self.add_files(project_list)

        # Publish project
        is_success_msg = ProjectUtility().publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Click 'Projects' menu
        is_clicked = project_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Delete project from server
        is_success_msg = ProjectUtility().delete_project_from_server(self.driver, project_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Click 'Projects' menu
        is_clicked = project_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Select project
        is_clicked = project_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Verify private lock icon absence
        is_verified = project_list.project_menu_component.check_private_lock_icon_absence()
        assert not is_verified, "Private lock icon is present"

        # Publish project
        is_success_msg = ProjectUtility().publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete local project
        is_success_msg = ProjectUtility().delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify project is not listed in project listing page
        is_verified = project_list.project_listing_component.verify_project_in_project_listing(project_title)
        assert is_verified, "Project is exist in the project listing page"

        # Delete project from server
        is_success_msg = ProjectUtility().delete_project_from_server(self.driver, project_title)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

    def add_files(self, project_list):
        """Logical separation of add files in to code data, input data and output data

        Args:
            project_list: The page with UI elements

        """
        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file into code data drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in to code data drop zone"

        # Click on Input Data tab
        is_clicked = project_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click Input Data tab"

        # Drag and drop text file into input drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_input_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in input drop zone"

        # Click on Output Data tab
        is_clicked = project_list.project_menu_component.click_output_data_tab()
        assert is_clicked, "Could not click Output Data tab"

        # Drag and drop text file into output drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_output_drop_zone('created')
        assert is_dropped, "Could not drag and drop text file in output drop zone"
