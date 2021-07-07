"""Test call for verify collaborators modifications appear in the activity feed"""
import pytest
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
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


@pytest.mark.verifyCollaboratorsModificationsAppearInActivityFeed
class TestVerifyCollaboratorsModificationsAppearInActivityFeed:
    """Includes test methods for verify collaborators modifications appear in the activity feed"""

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
    def test_verify_collaborators_modifications_appear_in_activity_feed(self, clean_up_project, server_data_fixture):
        """Test method to verify collaborators modifications appear in the activity feed"""
        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Instance of ProjectUtility class
        project_utility = ProjectUtility()

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

        # Fetch user credentials of user 2
        user2_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User2)

        # Fetch user credentials of user 1
        user1_credentials = ConfigurationManager.getInstance().get_user_credentials(server_data_fixture.server_id,
                                                                                    LoginUser.User1)
        # Collaborator name
        collaborator_name = user2_credentials.display_name

        # Current username
        username = user1_credentials.display_name

        # Add collaborator Read permission and verify activity feed
        self.add_collaborator_read_permission_and_verify(project_list, dataset_utility, collaborator_name, username)

        # Update collaborator permission to Read & Write  and verify activity feed
        self.update_collaborator_read_and_write_permission_and_verify(project_list, collaborator_name, username)

        # Update collaborator permission to Admin and verify activity feed
        self.update_collaborator_admin_permission_and_verify(project_list, collaborator_name, username)

        # Remove collaborator and verify activity feed
        self.remove_collaborator_and_verify(project_list, collaborator_name, username)

    def add_collaborator_read_permission_and_verify(self, project_list, dataset_utility, collaborator_name, username):
        """ Logical separation of add collaborator read permission and verify activity feed

        Args:
            project_list: The page with UI elements
            dataset_utility: Instance of DatasetUtility
            collaborator_name: Name of the collaborator
            username: Current username

        """
        # Add user2 as collaborator
        is_success_msg = dataset_utility.add_collaborator(self.driver, collaborator_name, 'Read')
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Wait to reload the activity feed
        time.sleep(5)

        # Click 'Activity' tab
        is_clicked = project_list.project_activity_component.click_activity_tab()
        assert is_clicked, "Could not click Activity tab"

        # Verify activity feed 'Adding collaborator with read-only permissions'
        is_verified = project_list.project_activity_component.verify_activity_feed \
            (f"Adding collaborator {collaborator_name} with read-only permissions")
        assert is_verified, "Could not verify activity feed 'Adding collaborator with read-only permissions'"

    def update_collaborator_read_and_write_permission_and_verify(self, project_list, collaborator_name, username):
        """ Logical separation of add collaborator read & write permission and verify activity feed

        Args:
            project_list: The page with UI elements
            collaborator_name: Name of the collaborator
            username: Current username

        """
        # Click on Collaborators button
        is_clicked = project_list.project_menu_component.click_collaborators_button()
        assert is_clicked, "Could not click Collaborators button"

        # Update collaborator permission
        is_clicked = project_list.collaborators_modal_component.update_collaborator_permission(
            collaborator_name, 'Write')
        assert is_clicked, "Updating collaborator to read & write permissions"

        # Click on collaborator modal close button
        is_clicked = project_list.collaborators_modal_component.click_collaborator_modal_close()
        assert is_clicked, "Could not close collaborator modal"

        # Click 'Overview' tab to reload the activity feed
        is_clicked = project_list.project_menu_component.click_overview_tab()
        assert is_clicked, "Could not click Overview tab"

        # Click 'Activity' tab
        is_clicked = project_list.project_activity_component.click_activity_tab()
        assert is_clicked, "Could not click Activity tab"

        # Verify activity feed 'Adding collaborator with read-only permissions'
        is_verified = project_list.project_activity_component.verify_activity_feed \
            (f"Updating collaborator {collaborator_name} to read & write permissions")
        assert is_verified, "Could not verify activity feed 'Adding collaborator with read-only permissions'"

    def update_collaborator_admin_permission_and_verify(self, project_list, collaborator_name, username):
        """ Logical separation of add collaborator Admin permission and verify activity feed

        Args:
            project_list: The page with UI elements
            collaborator_name: Name of the collaborator
            username: Current username

        """
        # Click on Collaborators button
        is_clicked = project_list.project_menu_component.click_collaborators_button()
        assert is_clicked, "Could not click Collaborators button"

        # Update collaborator permission to Admin
        is_clicked = project_list.collaborators_modal_component.update_collaborator_permission(
            collaborator_name, 'Admin')
        assert is_clicked, "Updating collaborator to Admin permissions"

        # Click on collaborator modal close button
        is_clicked = project_list.collaborators_modal_component.click_collaborator_modal_close()
        assert is_clicked, "Could not close collaborator modal"

        # Click 'Overview' tab to reload the activity feed
        is_clicked = project_list.project_menu_component.click_overview_tab()
        assert is_clicked, "Could not click Overview tab"

        # Click 'Activity' tab
        is_clicked = project_list.project_activity_component.click_activity_tab()
        assert is_clicked, "Could not click Activity tab"

        # Verify activity feed 'Adding collaborator with administrator permissions'
        is_verified = project_list.project_activity_component.verify_activity_feed \
            (f"Updating collaborator {collaborator_name} to administrator permissions")
        assert is_verified, "Could not verify activity feed 'Adding collaborator with administrator permissions'"

    def remove_collaborator_and_verify(self, project_list, collaborator_name, username):
        """ Logical separation of remove collaborator and verify activity feed

        Args:
            project_list: The page with UI elements
            collaborator_name: Name of the collaborator
            username: Current username

        """
        # Click on Collaborators button
        is_clicked = project_list.project_menu_component.click_collaborators_button()
        assert is_clicked, "Could not click Collaborators button"

        # Remove collaborator
        is_clicked = project_list.collaborators_modal_component.remove_collaborator(collaborator_name)
        assert is_clicked, "Remove collaborator"

        # Verify collaborator is removed
        is_clicked = project_list.collaborators_modal_component.verify_collaborator_is_removed(collaborator_name)
        assert is_clicked, f"Collaborator {collaborator_name} is not removed"

        # Click on collaborator modal close button
        is_clicked = project_list.collaborators_modal_component.click_collaborator_modal_close()
        assert is_clicked, "Could not close collaborator modal"

        # Click 'Overview' tab to reload the activity feed
        is_clicked = project_list.project_menu_component.click_overview_tab()
        assert is_clicked, "Could not click Overview tab"

        # Click 'Activity' tab
        is_clicked = project_list.project_activity_component.click_activity_tab()
        assert is_clicked, "Could not click Activity tab"

        # Verify activity feed 'Adding collaborator with administrator permissions'
        is_verified = project_list.project_activity_component.verify_activity_feed \
            (f"Removing collaborator {collaborator_name}")
        assert is_verified, "Could not verify activity feed 'Adding collaborator with administrator permissions'"
