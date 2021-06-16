"""Test call for exercise dataset file cache delete"""
import pytest
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from configuration.configuration import ConfigurationManager
from client_app.pages.landing.landing_page import LandingPage
from client_app.pages.dataset_listing.dataset_listing_page import DatasetListingPage
from framework.factory.models_enums.constants_enums import LoginUser
from tests.helper.dataset_utility import DatasetUtility
from tests.helper.project_utility import ProjectUtility
from tests.constants_enums.constants_enums import ProjectConstants
from collections import namedtuple
from tests.test_fixtures import clean_up_project
from tests.test_fixtures import clean_up_dataset
from tests.test_fixtures import clean_up_remote_dataset
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture
import time


@pytest.mark.datasetFileCacheDelete
class TestDatasetFileCacheDelete:
    """Includes test methods for basic dataset creation, file cache delete and its dependent tests"""

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
    def test_dataset_file_cache_delete(self, clean_up_project, clean_up_dataset, clean_up_remote_dataset):
        """Test method to create a dataset and file cache delete"""
        # Instance of DatasetUtility class
        dataset_utility = DatasetUtility()

        # Instance of ProjectUtility class
        project_utility = ProjectUtility()

        # Create dataset
        is_success_msg = dataset_utility.create_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Load dataset Listing Page
        dataset_list = DatasetListingPage(self.driver)
        assert dataset_list, "Could not load Dataset Listing Page"

        # Get dataset title
        dataset_title = dataset_list.project_menu_component.get_title()
        assert dataset_title is not None, "Could not get the dataset title"

        # Set dataset details into 'clean_up_remote_dataset' fixture
        dataset_details = {'dataset_name': dataset_title, 'driver': self.driver}
        clean_up_remote_dataset.update(dataset_details)

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"
        time.sleep(6)

        # Drag and drop text file with contents "created"
        is_dropped = dataset_list.dataset_data_component.drag_and_drop_text_file_in_data_drop_zone('file1', 'created')
        assert is_dropped, "Could not drop file1 into data drop zone"

        # Publish Dataset
        is_success_msg = dataset_utility.publish_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Create project
        is_success_msg = project_utility.create_project(self.driver, is_guide=False)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Get project title
        project_title1 = dataset_list.project_menu_component.get_title()
        assert project_title1 is not None, "Could not get the project title"

        # Link Dataset
        self.link_dataset(dataset_list, dataset_title)

        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        time.sleep(.5)

        # Create project
        is_success_msg = project_utility.create_project(self.driver, is_guide=False)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Get project title
        project_title2 = dataset_list.project_menu_component.get_title()
        assert project_title2 is not None, "Could not get the project title"

        # Link Dataset
        self.link_dataset(dataset_list, dataset_title)

        # Verify file content in input folder
        file_details = namedtuple('file_details', ('folder_name', 'dataset_name', 'file_name', 'file_content'))
        file1_details = file_details('input', dataset_title, 'file1', 'created')
        verification_message = dataset_utility.verify_file_content_in_jupyter_lab(self.driver, [file1_details])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Delete the dataset locally
        self.delete_dataset_locally(dataset_list, dataset_title, dataset_utility)

        # Verify file cache for the dataset exist
        is_verified = dataset_list.dataset_data_component.verify_dataset_file_cache(dataset_title)
        assert is_verified, "File cache for the dataset does not exist"

        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Select project
        is_clicked = dataset_list.project_listing_component.click_project(project_title1)
        assert is_clicked, "Could not click the project in project listing page"

        # Delete local project1
        is_success_msg = project_utility.delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify file cache for the dataset exist
        is_verified = dataset_list.dataset_data_component.verify_dataset_file_cache(dataset_title)
        assert is_verified, "File cache for the dataset does not exist"

        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Select project
        is_clicked = dataset_list.project_listing_component.click_project(project_title2)
        assert is_clicked, "Could not click the project in project listing page"

        # Delete local project1
        is_success_msg = project_utility.delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify file cache for the dataset exist
        for cnt in range(5):
            # File cache clean up happens via a background job. This may take a few seconds to complete.
            time.sleep(1)
            is_verified = dataset_list.dataset_data_component.verify_dataset_file_cache(dataset_title)
            if is_verified is False:
                break

        assert not is_verified, "File cache for the dataset still exist"

    def link_dataset(self, dataset_list, dataset_title):
        """Logical separation of link dataset functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the dataset

        """
        # Click on Input Data tab
        is_clicked = dataset_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click on Input Data tab"

        # Click on link dataset button
        is_clicked = dataset_list.code_input_output_data_component.click_link_dataset_button()
        assert is_clicked, "Could not click on link dataset button"

        # Select dataset from link dataset window
        is_selected = dataset_list.code_input_output_data_component.select_dataset(dataset_title)
        assert is_selected, "Could not select dataset from dataset link window"

        # Click on link dataset button on link dataset window
        is_clicked = dataset_list.code_input_output_data_component.click_link_dataset_button_on_link_dataset_window()
        assert is_clicked, "Could not click on link dataset button on link dataset window"

        # Check link dataset window closed
        is_closed = dataset_list.code_input_output_data_component.check_link_dataset_window_closed()
        assert is_closed, "Could not close link dataset window"

    def delete_dataset_locally(self, dataset_list, dataset_title, dataset_utility):
        """Logical separation of delete dataset functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the dataset
            dataset_utility: Instance of DatasetUtility class

        """
        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        assert dataset_list.dataset_listing_component.get_dataset_page_title() == "Datasets"

        # Check for the Add dataset title presence
        is_checked = dataset_list.dataset_listing_component.check_add_dataset_title_presence()
        assert is_checked, "Add dataset title is not present in the dataset listing page"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Delete dataset locally
        is_success_msg = dataset_utility.delete_dataset(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Verify dataset is not listed in project listing page
        is_verified = dataset_list.dataset_listing_component.verify_dataset_in_dataset_listing(dataset_title)
        assert is_verified, "Dataset is exist in the dataset listing page"
