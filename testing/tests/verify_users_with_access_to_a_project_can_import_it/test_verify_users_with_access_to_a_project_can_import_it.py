"""Test call for verify that only users with access to a project can import it"""
import pytest

from tests.helper.dataset_utility import DatasetUtility
from tests.helper.project_utility import ProjectUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.constants_enums.constants_enums import ProjectConstants
from tests.test_fixtures import clean_up_project, clean_up_remote_project
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
import time
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture


@pytest.mark.verifyUsersWithAccessToAProjectCanImportIt
class TestVerifyUsersWithAccessToAProjectCanImportIt:
    """Includes test methods for verify that only users with access to a project can import it"""

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
    def test_verify_users_with_access_to_a_project_can_import_it(self, clean_up_project, clean_up_remote_project,
                                                                 server_data_fixture):
        """Test method to verify that only users with access to a project can import it"""
        # Instance of ProjectUtility class
        project_utility = ProjectUtility()

        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Publish project
        is_success_msg = project_utility.publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Set project details into 'clean_up_remote_project' fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Click 'Projects' menu
        is_clicked = project_list.project_menu_component.click_project_menu_button()
        assert is_clicked, "Could not click Projects menu"

        # Get import URL
        import_url = project_list.project_menu_component.get_import_url()
        assert import_url is not None, "Could not get import URL"

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Try to import the project using import URL
        self.try_to_import(project_list, import_url)

        # Verify project import error pop up is shown
        is_verified = project_list.project_listing_component.verify_project_import_error()
        assert is_verified, "Could not verify project import error"

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Select Project
        is_clicked = project_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Check private lock icon presence
        is_checked = project_list.project_menu_component.check_private_lock_icon_presence()
        assert is_checked, "Could not found private lock icon presence"

        # Add user2 as collaborator
        is_success_msg = dataset_utility.add_collaborator(self.driver, user2_credentials.display_name, 'Read')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Switch user1 to user2
        is_success_msg = project_utility.switch_user(self.driver, user2_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Try to import the project using import URL
        self.try_to_import(project_list, import_url)

        # Verify project imported successfully
        is_verified = project_list.project_listing_component.verify_project_import_success()
        assert is_verified, "Could not verify project imported successfully"

        # Switch user2 to user1
        is_success_msg = project_utility.switch_user(self.driver, user1_credentials, server_data_fixture)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

    def try_to_import(self, project_list, import_url):
        """Logical separation of try to import project functionality

        Args:
            project_list: The page with UI elements
            import_url: URL of the project to be import

        """
        # Time sleep to make sure 'Import Existing' button is loaded fully
        time.sleep(3)

        # Click import existing button
        is_clicked = project_list.project_listing_component.click_import_existing_project_button()
        assert is_clicked, "Could not click import project existing button"

        # Type import URL into input area
        is_typed = project_list.project_listing_component.type_project_import_url(import_url)
        assert is_typed, "Could not type import URL"

        # Click import project button
        is_clicked = project_list.project_listing_component.click_import_project_button()
        assert is_clicked, "Could not click import project button"

