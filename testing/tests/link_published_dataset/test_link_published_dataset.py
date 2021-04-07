"""Test call for exercise linked published dataset"""
import time

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
from tests.test_fixtures import clean_up_remote_project
from tests.test_fixtures import clean_up_remote_dataset
from client_app.pages.login.login_factory import LoginFactory
from tests.test_fixtures import server_data_fixture
import time


@pytest.mark.linkPublishedDataset
class TestCreatePublishDataset:
    """Includes test methods for basic dataset creation, publish, link and its dependent tests"""

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
    def test_link_published_dataset(self, clean_up_project, clean_up_dataset, clean_up_remote_project,
                                    clean_up_remote_dataset):
        """Test method to create, publish and link a dataset"""
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
        time.sleep(3)

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
        project_title = dataset_list.project_menu_component.get_title()
        assert project_title is not None, "Could not get the project title"

        # Set project details into 'clean_up_remote_project' fixture
        project_details = {'project_name': project_title, 'driver': self.driver}
        clean_up_remote_project.update(project_details)

        # Link Dataset
        self.link_dataset(dataset_list, dataset_title)

        # Verify file content in input folder
        file_details = namedtuple('file_details', ('folder_name', 'dataset_name', 'file_name', 'file_content'))
        file1_details = file_details('input', dataset_title, 'file1', 'created')
        verification_message = dataset_utility.verify_file_content_in_jupyter_lab(self.driver, [file1_details])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

        # Publish project
        is_success_msg = project_utility.publish_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

        # Delete the project and dataset locally
        self.delete_project_and_dataset_locally(dataset_list, dataset_title, dataset_utility, project_utility)

        # Import project
        self.import_project_and_verify_dataset(dataset_list, project_title, dataset_title)

        # Download file
        self.download_file(dataset_list, project_title)

        # Verify file content in input folder
        file_details = namedtuple('file_details', ('folder_name', 'dataset_name', 'file_name', 'file_content'))
        file1_details = file_details('input', dataset_title, 'file1', 'created')
        verification_message = dataset_utility.verify_file_content_in_jupyter_lab(self.driver, [file1_details])
        assert verification_message == ProjectConstants.SUCCESS.value, verification_message

    def link_dataset(self, dataset_list, dataset_title):
        """Logical separation of delete project and dataset functionality

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

    def delete_project_and_dataset_locally(self, dataset_list, dataset_title, dataset_utility, project_utility):
        """Logical separation of delete project and dataset functionality

        Args:
            dataset_list: The page with UI elements
            dataset_title: Title of the dataset
            dataset_utility: Instance of DatasetUtility class
            project_utility: Instance of ProjectUtility class

        """
        # Delete local project
        is_success_msg = project_utility.delete_project(self.driver)
        assert is_success_msg == ProjectConstants.SUCCESS.value, is_success_msg

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

    def import_project_and_verify_dataset(self, dataset_list, project_title, dataset_title):
        """Logical separation of import project and verify dataset imported automatically

        Args:
            project_title: Title of the project
            dataset_list: The page with UI elements
            dataset_title: Title of the dataset

        """
        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Click server tab
        is_clicked = dataset_list.server_component.click_server_tab()
        assert is_clicked, "Could not click server tab"

        # Verify project in server page
        is_verified = dataset_list.server_component.verify_title_in_server(project_title)
        assert is_verified, "Could not verify project in server"

        # Click import button in server page
        is_clicked = dataset_list.server_component.click_project_import_button(project_title)
        assert is_clicked, "Could not click import button in server page"

        # Monitor container status to go through Stopped -> Building
        is_status_changed = dataset_list.container_status_component.monitor_container_status("Building", 60)
        assert is_status_changed, "Could not get Building status"

        # Monitor container status to go through Building -> Stopped
        is_status_changed = dataset_list.container_status_component.monitor_container_status("Stopped", 60)
        assert is_status_changed, "Could not get Stopped status"

        # Click dataset menu
        is_clicked = dataset_list.dataset_menu_component.click_datasets_menu()
        assert is_clicked, "Could not click dataset menu"

        # Verify dataset is listed in project listing page
        is_verified = dataset_list.dataset_listing_component.verify_dataset_in_dataset_listing(dataset_title)
        assert not is_verified, "Dataset is exist in the dataset listing page"

        # Select dataset
        is_clicked = dataset_list.dataset_listing_component.select_dataset(dataset_title)
        assert is_clicked, "Could not click the dataset in dataset listing page"

        # Click "Data" tab
        is_clicked = dataset_list.dataset_menu_component.click_data_tab()
        assert is_clicked, "Could not click Data tab"

        # Verify files need to be download
        is_verified = dataset_list.dataset_data_component.verify_download_all_files_button_is_enabled()
        assert is_verified, "Could not verify the files need to be download"

    def download_file(self, dataset_list, project_title):
        """Logical separation of download file

        Args:
            project_title: Title of the project
            dataset_list: The page with UI elements

        """
        # Click 'Projects' menu
        is_clicked = dataset_list.project_menu_component.click_projects_menu()
        assert is_clicked, "Could not click Projects menu"

        # Select project
        is_clicked = dataset_list.project_listing_component.click_project(project_title)
        assert is_clicked, "Could not click the project in project listing page"

        # Click on Input Data tab
        is_clicked = dataset_list.project_menu_component.click_input_data_tab()
        assert is_clicked, "Could not click on Input Data tab"

        # Click download all button on input data tab
        is_clicked = dataset_list.code_input_output_data_component.click_input_download_all_button()
        assert is_clicked, "Could not click on download all button on input data tab"

        # Check for the presence of download complete pop up
        is_checked = dataset_list.code_input_output_data_component.check_download_complete_pop_up_presence()
        assert is_checked, "Could not check for the presence of download complete pop up window"

        # Verify files are downloaded
        is_verified = dataset_list.code_input_output_data_component.verify_files_are_downloaded()
        assert is_verified, "Could not verify files are downloaded"
