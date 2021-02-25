import shutil
from client_app.constant_enums.constants_enums import GigantumConstants
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from configuration.configuration import ConfigurationManager
from framework.factory.models_enums.constants_enums import LoginUser
from string import Template
import requests


class DatasetHelperUtility(object):
    """Helper utility for dataset directory"""

    def delete_local_dataset(self) -> bool:
        """Removes the dataset directory"""
        directories = ['datasets']
        self.__clean_up_cache()
        for directory in directories:
            self.__delete_directory(directory)
        return True

    def __delete_directory(self, directory_name: str) -> bool:
        """Deletes project directory.

        Args:
            directory_name: Name of the directory to remove
        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        user_directory = dataset_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / dataset_folder_names.\
            default_server / dataset_folder_names.username / dataset_folder_names.username / directory_name
        user_datasets = user_directory.glob('d-*')
        if user_datasets:
            for dataset in user_datasets:
                if dataset.exists():
                    shutil.rmtree(user_directory / dataset.name)
        return True

    def __clean_up_cache(self) -> bool:
        """Removes the dataset's file cache"""
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        user_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / \
                         GigantumConstants.DATASETS_FOLDER.value / dataset_folder_names.default_server / \
                         dataset_folder_names.username / dataset_folder_names.username
        datasets_cache = user_directory.glob('d-*')
        if datasets_cache:
            for dataset in datasets_cache:
                if dataset.exists():
                    shutil.rmtree(user_directory / dataset.name)
        return True

    def delete_remote_dataset(self, dataset_title, driver) -> None:
        """Method to remove remote dataset if it exists in the hub.

        Args:
            dataset_title: name of the Project to delete
            driver: driver instance

        """
        if ConfigurationManager.getInstance().get_app_setting("api_url"):
            api_url = ConfigurationManager.getInstance().get_app_setting("api_url")
        else:
            raise Exception("Unable to identify api url from configuration")
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(LoginUser.User1)
        namespace = user_credentials.user_name
        access_token = driver.execute_script("return window.localStorage.getItem('access_token')")
        id_token = driver.execute_script("return window.localStorage.getItem('id_token')")
        headers = {
            'Identity': id_token,
            'Authorization': f'Bearer {access_token}'
        }  # Build query
        query_template = Template("""
        mutation DeleteRemoteDataset {
          deleteDataset(input: {owner: "$owner", datasetName: "$dataset", remote: true}) {
            remoteDeleted
          }
        }
        """)
        query_str = query_template.substitute(owner=namespace, dataset=dataset_title)
        result = requests.post(api_url, json={'query': query_str}, headers=headers)
        if result.status_code != 200:
            raise Exception(f"Request to hub API failed. Status Code: {result.status_code}")
        result_data = result.json()
        if 'errors' in result_data:
            raise Exception("Failed to delete remote dataset")
        else:
            if result_data['data']['deleteDataset']['remoteDeleted'] is False:
                raise Exception("Failed to delete remote dataset")
