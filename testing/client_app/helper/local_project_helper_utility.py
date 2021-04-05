import json
import tempfile
from pathlib import Path
import shutil
import docker
import os
from configuration.configuration import ConfigurationManager
from framework.factory.models_enums.constants_enums import LoginUser
from client_app.constant_enums.constants_enums import GigantumConstants
from collections import namedtuple
from string import Template
import requests


class ProjectHelperUtility(object):
    """Helper utility for project directory"""

    def delete_local_project(self) -> bool:
        """Removes the project directories"""
        directories = ['labbooks']
        self.__stop_containers()
        self.__delete_local_images()
        for directory in directories:
            self.__delete_directory(directory)
        return True

    def __stop_containers(self) -> bool:
        """Stops the project containers"""
        containers = docker.from_env().containers.list()
        for container in containers:
            for tag in container.image.tags:
                if 'gmlb-' in tag:
                    container.stop()
        docker.from_env().containers.prune()
        return True

    def __delete_local_images(self) -> bool:
        """Removes the local project images"""
        server_details = self.get_server_details()
        images = docker.from_env().images.list()
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(server_details['server_id'], LoginUser.User1)
        username = user_credentials.display_name
        username_str = f"{username}-{username}"
        for image in images:
            for tag in image.tags:
                if 'gmlb-' in tag and 'p-' in tag and username_str in tag:
                    docker.from_env().images.remove(image.id, force=True, noprune=False)
        return True

    def __delete_directory(self, directory_name: str) -> bool:
        """Deletes project directory.

        Args:
            directory_name: Name of the directory to remove
        """
        server_details = self.get_server_details()
        project_folder_names = self.get_folder_names()
        user_directory = project_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / \
                         server_details['server_id'] / project_folder_names.username / project_folder_names.username / \
                         directory_name
        user_projects = user_directory.glob('p-*')
        if user_projects:
            for project in user_projects:
                if project.exists():
                    shutil.rmtree(user_directory / project.name)
        return True

    def check_project_removed_from_disk(self, project_title) -> bool:
        """  Verify whether the project is present in the disk or not

        Args:
            project_title: Title of the project to be checked

        Returns: returns the result of verification

        """
        project_folder_names = self.get_folder_names()
        user_directory = project_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / project_folder_names.\
            server_name / project_folder_names.username / project_folder_names.username / GigantumConstants.\
            PROJECTS_FOLDER.value
        user_projects = user_directory.glob('p-*')
        if user_projects:
            for project in user_projects:
                if project.exists():
                    if project.name == project_title:
                        return False
        return True

    def check_project_image_is_removed(self, project_title) -> bool:
        """ Verify project image is exist or not

        Args:
            project_title: Title of the current project

        Returns: returns the result of project image verification

        """
        images = docker.from_env().images.list()
        for image in images:
            for tag in image.tags:
                if 'gmlb-' in tag and project_title in tag:
                    return False
        return True

    def move_file_to_untracked_folder(self, folder_name, project_title):
        """ Move file to untracked folder

        Args:
            folder_name: Name of the folder
            project_title: Title of the current project

        Returns: returns the result of file move

        """
        project_folder_names = self.get_folder_names()
        file_path = project_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / project_folder_names.\
            server_name / project_folder_names.username / project_folder_names.username/ GigantumConstants.\
            PROJECTS_FOLDER.value / project_title / folder_name
        source = file_path / GigantumConstants.DEFAULT_FILE_NAME.value
        destination = file_path / GigantumConstants.UNTRACKED_FOLDER.value / GigantumConstants.DEFAULT_FILE_NAME.value
        if file_path:
            shutil.move(source, destination)
            return True
        return False

    def verify_untracked_directory_is_empty(self, project_title) -> bool:
        """ Verify untracked directories are empty or not

        Returns: returns the result of verification

        """
        directories = ['code', 'input', 'output']
        project_folder_names = self.get_folder_names()
        user_directory = project_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / project_folder_names.\
            server_name / project_folder_names.username / project_folder_names.username / GigantumConstants.\
            PROJECTS_FOLDER.value / project_title
        for directory in directories:
            # Since the untracked folder already contains a hidden file, len() = 1
            if len(os.listdir(user_directory / directory / GigantumConstants.UNTRACKED_FOLDER.value)) > 1:
                return False
        return True

    def verify_file_content(self, folder_name, file_content, project_title, is_collaborator=False):
        """ Verify file content in the project folders

        Args:
            folder_name: Name of the folder in which file is kept
            file_content: Content of the file
            project_title: Title of the current project
            is_collaborator: Decision variable to determine whether user is a collaborator or not

        Returns:

        """
        project_folder_names = self.get_folder_names()
        if is_collaborator:
            collaborator_credentials = ConfigurationManager.getInstance().get_user_credentials(
                project_folder_names.server_name, LoginUser.User2)
            username = collaborator_credentials.display_name
        else:
            username = project_folder_names.username
        file_directory = project_folder_names.home_dir / GigantumConstants.SERVERS_FOLDER.value / project_folder_names.\
            server_name / username / project_folder_names.username / GigantumConstants.\
            PROJECTS_FOLDER.value / project_title / folder_name / GigantumConstants.DEFAULT_FILE_NAME.value
        file = open(file_directory, "r")
        file_content_in_folder = str(file.read()).strip()
        if file_content_in_folder != file_content.strip():
            return False
        return True

    def get_folder_names(self) -> namedtuple:
        """ Return folder names for project path creation

        Returns: returns folder names as namedtuple

        """
        server_details = self.get_server_details()
        folder_names = namedtuple('folder_names', ('username', 'home_dir', 'server_name'))
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(server_details['server_id'],
                                                                                   LoginUser.User1)
        username = user_credentials.display_name
        home_dir = Path(GigantumConstants.HOME_DIRECTORY.value).expanduser()
        server_name = server_details['server_id']
        project_folder_names = folder_names(username, home_dir, server_name)
        return project_folder_names

    def delete_remote_project(self, project_title, driver) -> None:
        """Method to remove remote project if it exists in the hub.

        Args:
            project_title: name of the Project to delete
            driver: driver instance

        """
        server_details = self.get_server_details()
        if ConfigurationManager.getInstance().get_app_setting("api_url"):
            api_url = ConfigurationManager.getInstance().get_app_setting("api_url")
        else:
            raise Exception("Unable to identify api url from configuration")
        user_credentials = ConfigurationManager.getInstance().get_user_credentials(server_details['server_id'],
                                                                                   LoginUser.User1)
        namespace = user_credentials.display_name
        # Set headers
        access_token = driver.execute_script("return window.localStorage.getItem('access_token')")
        id_token = driver.execute_script("return window.localStorage.getItem('id_token')")
        headers = {
            'Identity': id_token,
            'Authorization': f'Bearer {access_token}'
        }
        # Build query
        query_template = Template("""
                            mutation DeleteRemoteProject {
                            deleteRemoteLabbook(input: {owner: "$owner", labbookName: "$project", confirm: true}) {
                            success
                                }
                                }
                            """)
        query_str = query_template.substitute(owner=namespace, project=project_title)
        result = requests.post(api_url, json={'query': query_str}, headers=headers)
        if result.status_code != 200:
            raise Exception(f"Request to hub API failed. Status Code: {result.status_code}")
        result_data = result.json()
        if 'errors' in result_data:
            raise Exception("Failed to delete remote project")
        else:
            if result_data['data']['deleteRemoteLabbook']['success'] is False:
                raise Exception("Failed to delete remote project")

    def set_server_details(self, server_details):
        """ Write server details into temporary file

        Args:
            server_details: Details of the current server
        """
        temp_dir = tempfile.gettempdir()
        server_details_dict = {'server_id': server_details.server_id, 'server_name': server_details.server_name,
                               'login_type': server_details.login_type}
        json_data = json.dumps(server_details_dict)
        with open(os.path.join(temp_dir, 'server_details'), 'w') as temp_file:
            temp_file.write(json_data)

    def get_server_details(self):
        """ Read temporary file and return server details

        Returns: returns current server details

        """
        temp_dir = tempfile.gettempdir()
        server_details_file = os.path.join(temp_dir, 'server_details')
        if not os.path.exists(server_details_file):
            raise Exception("Server details file is not available")
        with open(os.path.join(temp_dir, 'server_details'), 'r') as temp_file:
            json_data = json.load(temp_file)
            return json_data
