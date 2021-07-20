"""Test call for verify basic branch operations"""
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


@pytest.mark.verifyBasicBranchOperations
class TestVerifyBasicBranchOperations:
    """Includes test methods for verify basic branch operations"""

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
    def test_verify_basic_branch_operations(self, clean_up_project):
        """Test method to verify basic branch operations"""
        # Create project
        is_success_msg = ProjectUtility().create_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load Project Listing Page
        project_list = ProjectListingPage(self.driver)
        assert project_list is not None, "Could not load Project Listing Page"

        # Get project title
        project_title = project_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"
        time.sleep(1)

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file 'test1.txt' into code data drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_drop_zone\
            (file_name='test1.txt')
        assert is_dropped, "Could not drag and drop text 'test1.txt' file in to code data drop zone"

        # Create new branch 'test-branch'
        branch_title = 'test-branch'
        branch_description = 'test-branch-description'
        is_success_msg = ProjectUtility().create_branch_via_header(self.driver, branch_title, branch_description)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify branch name
        branch_name = project_list.project_branch_component.get_current_branch()
        assert branch_name == branch_title, "Could not verify branch title"
        time.sleep(1)

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Drag and drop text file 'test2.txt' into code data drop zone
        is_dropped = project_list.code_input_output_component.drag_and_drop_text_file_in_code_file_browser\
            (file_name='test2.txt')
        assert is_dropped, "Could not drag and drop text 'test2.txt' file in to code data drop zone"

        # Switch branch to 'master' and verify file
        self.switch_to_master_branch_and_verify_file(project_list)

        # Switch branch to 'test-master' and verify file
        self.switch_to_test_branch_and_verify_file(project_list)

        # Merge 'test-branch' into 'master'
        self.merge_test_branch_into_master_and_verify_files(project_list)

        # Delete 'test-branch' and verify files
        self.delete_test_branch_and_verify(project_list)

    def switch_to_master_branch_and_verify_file(self, project_list):
        """Logical separation of switch branch to 'master' and verify file

        Args:
            project_list: The page with UI elements

        """
        # Switch branch to 'master'
        is_switched = project_list.project_branch_component.switch_branch('master')
        assert is_switched, "Could not switch branch to 'master'"

        # Check for the branch switch complete pop up presence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_presence()
        assert is_checked, "Could not found the presence of branch switch complete pop up presence"

        # Check for the branch switch complete pop up absence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_absence()
        assert is_checked, "Branch switch complete pop up is not closed"

        # Click on Code Tab
        is_clicked = project_list.project_menu_component.click_code_data_tab()
        assert is_clicked, "Could not click Code tab"

        # Verify file 'test2.txt' is not present
        is_verified = project_list.code_input_output_component.verify_file_is_absent('test2.txt')
        assert is_verified, "File 'test2.txt' is still present"

    def switch_to_test_branch_and_verify_file(self, project_list):
        """Logical separation of switch branch to 'test-branch' and verify file

        Args:
            project_list: The page with UI elements

        """
        # Switch branch to 'test-branch'
        is_switched = project_list.project_branch_component.switch_branch('test-branch')
        assert is_switched, "Could not switch branch to 'test-branch'"

        # Check for the branch switch complete pop up presence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_presence()
        assert is_checked, "Could not found the presence of branch switch complete pop up presence"

        # Check for the branch switch complete pop up absence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_absence()
        assert is_checked, "Branch switch complete pop up is not closed"

        # Verify file 'test2.txt' is present
        is_verified = project_list.code_input_output_component.verify_file_is_present('test2.txt')
        assert is_verified, "File 'test2.txt' is not present"

        # Click delete button for file 'test1.txt'
        is_deleted = project_list.code_input_output_component.click_file_delete('test1.txt')
        assert is_deleted, "Could not click delete button for file 'test1.txt'"

    def merge_test_branch_into_master_and_verify_files(self, project_list):
        """Logical separation of merge 'test-branch' into 'master' and verify files

        Args:
            project_list: The page with UI elements

        """
        # Switch branch to 'master'
        is_switched = project_list.project_branch_component.switch_branch('master')
        assert is_switched, "Could not switch branch to 'master'"

        # Check for the branch switch complete pop up presence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_presence()
        assert is_checked, "Could not found the presence of branch switch complete pop up presence"

        # Check for the branch switch complete pop up absence
        is_checked = project_list.project_branch_component.check_branch_switch_complete_pop_up_absence()
        assert is_checked, "Branch switch complete pop up is not closed"

        # Click manage branches button
        is_clicked = project_list.project_branch_component.click_manage_branches_button()
        assert is_clicked, "Could not click manage branches button"

        # Move mouse focus to branch 'test-branch'
        is_moved = project_list.project_branch_component.move_to_branch('test-branch')
        assert is_moved, "Could not move mouse focus to branch 'test-branch'"

        # Click merge button on branch 'test-branch'
        is_merge_button_clicked = project_list.project_branch_component.click_branch_merge_button('test-branch')
        assert is_merge_button_clicked, "Could not click merge button on branch 'test-branch'"

        # Click branch merge confirm button
        is_clicked = project_list.project_branch_component.click_branch_merge_confirm_button()
        assert is_clicked, "Could not click branch merge confirm button"

        # Check for the presence of create branch icon
        is_checked = project_list.project_branch_component.check_create_branch_icon_presence()
        assert is_checked, "Could not get the create branch icon presence"

        # Verify file 'test1.txt' is not present
        is_verified = project_list.code_input_output_component.verify_file_is_absent('test1.txt')
        assert is_verified, "File 'test1.txt' is still present"

        # Verify file 'test2.txt' is present
        is_verified = project_list.code_input_output_component.verify_file_is_present('test2.txt')
        assert is_verified, "File 'test2.txt' is not present"

    def delete_test_branch_and_verify(self, project_list):
        """Logical separation of delete 'test-branch' and verify files

        Args:
            project_list: The page with UI elements

        """
        # Move mouse focus to branch 'test-branch'
        is_moved = project_list.project_branch_component.move_to_branch('test-branch')
        assert is_moved, "Could not move mouse focus to branch 'test-branch'"
        time.sleep(1)

        # Click delete button on branch 'test-branch'
        is_merge_button_clicked = project_list.project_branch_component.click_branch_trash_icon_button('test-branch')
        assert is_merge_button_clicked, "Could not click trash icon button on branch 'test-branch'"

        # Click branch delete local checkbox
        is_checkbox_clicked = project_list.project_branch_component.click_branch_delete_local_checkbox()
        assert is_checkbox_clicked, "Could not click branch delete local checkbox"

        # Click branch delete confirm button
        is_clicked = project_list.project_branch_component.click_delete_branch_confirm_button()
        assert is_clicked, "Could not click branch delete confirm button"

        # Check for the presence of create branch icon
        is_checked = project_list.project_branch_component.check_create_branch_icon_presence()
        assert is_checked, "Could not get the create branch icon presence"

        # Verify 'test-branch' is deleted
        is_verified = project_list.project_branch_component.verify_branch_presence('test-branch')
        time.sleep(1)
        assert not is_verified, "'test-branch' is not deleted successfully"
