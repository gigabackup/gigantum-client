import os
from collections import namedtuple
import pytest
import requests
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.helper.local_dataset_helper_utility import DatasetHelperUtility
from configuration.configuration import ConfigurationManager


server_details_tuple = namedtuple('server_details', ('server_name', 'server_id', 'login_type'))


@pytest.fixture()
def clean_up_project():
    """Remove containers and directory fixture."""
    yield
    ProjectHelperUtility().delete_local_project()


@pytest.fixture()
def clean_up_remote_project():
    """Remove remote project directory"""
    project_details = {}
    yield project_details
    if project_details:
        ProjectHelperUtility().delete_remote_project(project_details['project_name'], project_details['driver'])
    else:
        raise Exception("Failed to set project details into remote project clean up fixture")


@pytest.fixture()
def clean_up_dataset():
    """Remove local dataset directory"""
    yield
    DatasetHelperUtility().delete_local_dataset()


@pytest.fixture()
def clean_up_remote_dataset():
    """Remove remote dataset directory"""
    dataset_details = {}
    yield dataset_details
    if dataset_details:
        DatasetHelperUtility().delete_remote_dataset(dataset_details['dataset_name'], dataset_details['driver'])
    else:
        raise Exception("Failed to set dataset details into remote dataset clean up fixture")


@pytest.fixture(scope='session')
def server_data_fixture() -> server_details_tuple:
    """Load the server data for the selected server"""
    server_id = os.environ.get("SERVER_ID")
    if not server_id:
        server_id = 'gigantum-com'

    if ConfigurationManager.getInstance().get_app_setting("server_api_url"):
        api_url = ConfigurationManager.getInstance().get_app_setting("server_api_url")
    else:
        raise Exception("Unable to identify api url from configuration")

    result = requests.get(api_url)
    if result.status_code != 200:
        raise Exception(f"Request to Client API failed. Status Code: {result.status_code}")
    result_data = result.json()

    server_details = None
    for server_details_dict in result_data.get('available_servers'):
        if server_details_dict.get('server_id') == server_id:
            login_url = server_details_dict['login_url']
            login_url = login_url.replace('auth/redirect?target=login', '.well-known/auth.json')
            result = requests.get(login_url, verify=False)
            if result.status_code != 200:
                raise Exception(f"Request to hub API failed. Status Code: {result.status_code}")
            login_data = result.json()
            if 'login_type' in login_data:
                server_details = server_details_tuple(server_details_dict['name'],
                                                      server_details_dict['server_id'],
                                                      login_data['login_type'])
                break

    yield server_details
