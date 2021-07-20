"""Test call for verify a local branch can be created successfully"""
import pytest
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.verifyLocalBranchCreatedSuccessfully
class TestVerifyLocalBranchCreatedSuccessfully:
    """Includes test methods for verify a local branch can be created successfully"""

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
    def test_verify_local_branch_created_successfully(self, clean_up_project):
        """Test method to verify a local branch can be created successfully"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Create new branch 'test-branch1' via header
        branch_title1 = 'test-branch1'
        branch_description1 = 'test-branch-description1'
        is_success_msg = ProjectUtility().create_branch_via_header(self.driver, branch_title1, branch_description1)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify branch name
        branch_name = project_list.project_branch_component.get_current_branch()
        assert branch_name == branch_title1, "Could not verify branch title"

        # Create new branch 'test-branch2' via manage menu
        branch_title2 = 'test-branch2'
        branch_description2 = 'test-branch-description2'
        is_success_msg = ProjectUtility().create_branch_via_manage_menu(self.driver, branch_title2, branch_description2)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify branch name
        branch_name = project_list.project_branch_component.get_current_branch()
        assert branch_name == branch_title2, "Could not verify branch title"
