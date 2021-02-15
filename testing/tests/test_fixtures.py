import pytest
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from client_app.helper.local_dataset_helper_utility import DatasetHelperUtility


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
