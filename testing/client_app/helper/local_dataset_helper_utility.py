import shutil
import tempfile
from client_app.constant_enums.constants_enums import GigantumConstants
from client_app.helper.local_project_helper_utility import ProjectHelperUtility
from configuration.configuration import ConfigurationManager
from framework.factory.models_enums.constants_enums import LoginUser
from string import Template
import requests
import subprocess
import os
from selenium import webdriver


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
            server_name / dataset_folder_names.username / dataset_folder_names.username / directory_name
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
                         GigantumConstants.DATASETS_FOLDER.value / dataset_folder_names.server_name / \
                         dataset_folder_names.username / dataset_folder_names.username
        datasets_cache = user_directory.glob('d-*')
        if datasets_cache:
            for dataset in datasets_cache:
                if dataset.exists():
                    shutil.rmtree(user_directory / dataset.name)
        return True

    def delete_remote_dataset(self, dataset_title: str, driver: webdriver) -> None:
        """Method to remove remote dataset if it exists in the hub.

        Args:
            dataset_title: name of the Project to delete
            driver: driver instance

        """
        server_details = ProjectHelperUtility().get_server_details()
        if ConfigurationManager.getInstance().get_app_setting("api_url"):
            api_url = ConfigurationManager.getInstance().get_app_setting("api_url")
        else:
            raise Exception("Unable to identify api url from configuration")
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(server_details['server_id'],
                                                                                   LoginUser.User1)
        namespace = user_credentials.display_name
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

    def get_hash_code(self, dataset_title: str) -> str:
        """ Get the git hash code

        Args:
            dataset_title: Title of the dataset

        Returns: return hash code

        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        working_directory = dataset_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / \
                            dataset_folder_names.server_name / dataset_folder_names.username / \
                            dataset_folder_names.username / GigantumConstants.DATASETS_FOLDER.value / dataset_title
        out = subprocess.Popen(['git', 'rev-list', 'HEAD', '--max-count=1'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, cwd=working_directory)
        stdout, stderr = out.communicate()
        return str(stdout.decode("utf-8").strip("\n"))

    def add_file(self, file_name: str, file_content: str, folder_name: str, dataset_name: str, hash_code_folder: str,
                 sub_folder_name: str) -> bool:
        """ Add text files into the dataset folder

        Args:
            file_name: Name of the file to be add
            file_content: Content of the file to be add
            folder_name: Name of the folder in which file to be added
            dataset_name: Name of the dataset
            hash_code_folder: Folder in which files need to be placed
            sub_folder_name: Name of the sub folder

        Returns: returns the result of file adding

        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        if sub_folder_name:
            file_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / GigantumConstants. \
                DATASETS_FOLDER.value / dataset_folder_names.server_name / dataset_folder_names.username / \
                             dataset_folder_names.username / dataset_name / hash_code_folder / folder_name / sub_folder_name
        else:
            file_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / GigantumConstants. \
                DATASETS_FOLDER.value / dataset_folder_names.server_name / dataset_folder_names.username / \
                             dataset_folder_names.username / dataset_name / hash_code_folder / folder_name
        temp_dir = tempfile.gettempdir()
        with open(os.path.join(temp_dir, file_name), 'w') as temp_file:
            temp_file.write(file_content)
        file_path = os.path.join(temp_dir, file_name)
        if file_path:
            shutil.move(file_path, file_directory)
            return True
        return True

    def add_binary_file_to_root(self, file_name: str, size_in_mb: int, dataset_name: str, hash_code_folder: str,
                                random_contents: bool = False) -> bool:
        """ Add binary file into the dataset folder

        Args:
            file_name: Name of the file to be add
            size_in_mb: Size of the file in MBs
            dataset_name: Name of the dataset
            hash_code_folder: Folder in which files need to be placed
            random_contents: True for random file, False for all 0's

        Returns: returns the result of file adding

        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        file_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / GigantumConstants. \
            DATASETS_FOLDER.value / dataset_folder_names.server_name / dataset_folder_names.username / \
                         dataset_folder_names.username / dataset_name / hash_code_folder
        temp_dir = tempfile.gettempdir()
        with open(os.path.join(temp_dir, file_name), 'wb') as temp_file:
            if random_contents:
                for _ in range(size_in_mb):
                    temp_file.write(os.urandom(1000 * 1000))
            else:
                for _ in range(size_in_mb):
                    temp_file.write(b"0" * 1000 * 1000)

        file_path = os.path.join(temp_dir, file_name)
        if file_path:
            shutil.move(file_path, file_directory)
            return True
        return True

    def update_file_content(self, file_name: str, file_content: str, dataset_name: str, hash_code_folder: str) -> bool:
        """ Update the content of file

        Args:
            file_name: Name of the file to be add
            file_content: Content of the file to be add
            dataset_name: Name of the dataset
            hash_code_folder: Folder in which files need to be placed

        Returns: returns the result of file update operation
        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        file_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / GigantumConstants. \
            DATASETS_FOLDER.value / dataset_folder_names.server_name / dataset_folder_names.username / \
                         dataset_folder_names.username / dataset_name / hash_code_folder
        with open(os.path.join(file_directory, file_name), 'w') as temp_file:
            temp_file.seek(0)
            temp_file.truncate()
            temp_file.write(file_content)
        return True

    def verify_dataset_file_cache(self, dataset_name: str) -> bool:
        """Verify whether the dataset file cache is present or not

        Args:
            dataset_name: Name of the dataset to be verify

        Returns: returns the result of verification

        """
        dataset_folder_names = ProjectHelperUtility().get_folder_names()
        user_directory = dataset_folder_names.home_dir / GigantumConstants.CACHE_FOLDER.value / \
                         GigantumConstants.DATASETS_FOLDER.value / dataset_folder_names.server_name / \
                         dataset_folder_names.username / dataset_folder_names.username
        datasets_cache = user_directory.glob('d-*')
        if datasets_cache:
            for dataset in datasets_cache:
                if dataset.name == dataset_name:
                    return True
        return False
