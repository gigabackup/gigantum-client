import os
import platform
import re
import glob
import datetime
import sys

from docker.errors import ImageNotFound, NotFound, APIError
import yaml
import requests
from natsort import natsorted
import shutil

from gtm.common.console import ask_question
from gtm.utils import get_docker_client, get_current_commit_hash
from gtm.common import get_client_root


class ClientBuilder(object):
    """Class to manage building the gigantum client container
    """

    def __init__(self, image_name: str):
        """Constructor"""
        self.image_name = image_name
        self._container_name = None
        self.docker_client = get_docker_client()

    @staticmethod
    def _remove_pyc(directory: str) -> None:
        """Method to remove all pyc files recursively

        Args:
            directory(str) Root directory to walk
        """
        for filename in glob.glob('{}/**/*.pyc'.format(directory), recursive=True):
            os.remove(filename)

    @staticmethod
    def _remove_mypy_cache(client_root_dir: str) -> None:
        """Method to remove mypy cache dirs
        """
        shutil.rmtree(os.path.join(client_root_dir, "packages", "gtmapi", ".mypy_cache"), ignore_errors=True)
        shutil.rmtree(os.path.join(client_root_dir, "packages", "gtmcore", ".mypy_cache"), ignore_errors=True)

    @staticmethod
    def get_image_tag() -> str:
        """Method to generate a named tag for the Docker Image

        Returns:
            str
        """
        return get_current_commit_hash(8)

    def _generate_container_name(self) -> str:
        """Method to generate a name for the Docker container

        Returns:
            str
        """
        return self.image_name.replace("/", ".")

    @property
    def container_name(self) -> str:
        """Get the name of the LabManager container

        Returns:
            str8
        """
        if not self._container_name:
            # using the setter forces a check that we have a valid name
            self.container_name = self._generate_container_name()
        return self._container_name

    @container_name.setter
    def container_name(self, value: str) -> None:
        # Validate
        if not re.match("^(?![-.])(?!.*--)[A-Za-z0-9_.-]+(?<![-.])$", value):
            raise ValueError(
                "Invalid container name. Only A-Za-z0-9._- allowed w/ no leading/trailing hyphens/periods.")

        self._container_name = value

    def image_exists(self, name) -> bool:
        """Method to check if a Docker image exists

        Returns:
            bool
        """
        # Check if image exists
        try:
            self.docker_client.images.get(name)
            return True
        except ImageNotFound:
            return False

    def remove_image(self, image_name: str) -> None:
        """Remove a docker image by name

        Args:
            image_name(str): Name of the docker image to remove
        """
        # Remove stopped container if it exists
        self.prune_container(image_name)

        # Remove image
        self.docker_client.images.remove(image_name)

    @staticmethod
    def merge_requirements_files(source_files) -> None:
        """Method to merge requirements.txt files into a single file for build purposes. This simplifies build process
        and also lets the app build with additional dependencies when needed (e.g. test)

        Args:
            source_files(list): List of relative file paths to requirement.txt files
        """
        build_dir = os.path.join(get_client_root(), 'build')
        if os.path.exists(build_dir) is False:
            os.makedirs(build_dir)

        output = ""
        for f in source_files:
            with open(os.path.join(get_client_root(), f), 'rt') as fd:
                output = f"{output}{fd.read()}\n\n"

        with open(os.path.join(get_client_root(), 'build', 'requirements-testing.txt'), 'wt') as fw:
            fw.write(output)

    @staticmethod
    def write_empty_testing_requirements_file() -> None:
        """Method to merge requirements.txt files into a single file for build purposes. This simplifies build process
        and also lets the app build with additional dependencies when needed (e.g. test)
        """
        build_dir = os.path.join(get_client_root(), 'build')
        if os.path.exists(build_dir) is False:
            os.makedirs(build_dir)

        with open(os.path.join(get_client_root(), 'build', 'requirements-testing.txt'), 'wt') as fw:
            fw.write("")

    def prune_container(self, container_name: str) -> None:
        """Remove a docker container by name

        Args:
            container_name(str): Name of the docker container to remove
        """
        # Remove stopped container if it exists
        try:
            # Replace / with . if the repo is in the image name
            container_name = container_name.replace("/", ".")

            build_container = self.docker_client.containers.get(container_name)
            build_container.remove()
        except NotFound:
            pass
        except requests.exceptions.ChunkedEncodingError:
            pass

    def build_image(self, no_cache: bool = False, build_args: dict = None, docker_args: dict = None) -> None:
        """Method to build the Gigantum Client Docker Image

        Args:
            no_cache: Flag indicating if the docker cache should be ignored
            build_args: Variables to prepare files for build
            docker_args: Variables passed to docker during the build process

        build_args items:
            supervisor_file: The path to the target supervisor file to move into build dir
            config_override_file: The path to the target config file override file

        docker_args items:
            CLIENT_CONFIG_FILE: The client config file
            NGINX_UI_CONFIG: Nginx config file for the UI
            NGINX_API_CONFIG: Nginx config file for the API
            SUPERVISOR_CONFIG: Supervisord config file
            ENTRYPOINT_FILE: Entrypoint file
        """
        # Check if *nix or windows
        # Doing this at the top of the function so it's clear this variable is
        # available
        if platform.system() == 'Windows':
            is_windows = True
        else:
            is_windows = False

        self.docker_client = get_docker_client()
        client_root_dir = get_client_root()
        build_dir = os.path.join(client_root_dir, build_args['build_dir'])
        if os.path.exists(build_dir) is False:
            os.makedirs(build_dir)

        named_image = "{}:{}".format(self.image_name, self.get_image_tag())
        if self.image_exists(named_image):
            # Image found. Make sure container isn't running.
            self.prune_container(named_image)

        # Write updated config file
        base_config_file = os.path.join(client_root_dir, "packages", 'gtmcore', 'gtmcore',
                                        'configuration', 'config', 'labmanager.yaml.default')
        final_config_file = docker_args['CLIENT_CONFIG_FILE']

        with open(base_config_file, "rt") as cf:
            base_data = yaml.safe_load(cf)
        with open(os.path.join(client_root_dir, build_args['config_override_file']), "rt") as cf:
            overwrite_data = yaml.safe_load(cf)

        # Merge sub-sections together
        for key in base_data:
            if key in overwrite_data:
                base_data[key].update(overwrite_data[key])

        # Add Build Info
        build_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        short_hash = get_current_commit_hash()[:8]
        releases = list()
        for release in glob.glob(os.path.join(client_root_dir, "changelog", "releases", "*")):
            releases.append(release)
        releases = natsorted(releases)
        _, release_version = releases[-1].split("/releases/v")
        base_data['build_info'] = f"Gigantum Client :: {build_date} :: {short_hash} :: {release_version}"

        # Write out updated config file
        with open(os.path.join(client_root_dir, final_config_file), "wt") as cf:
            cf.write(yaml.dump(base_data, default_flow_style=False))

        # Write final supervisor file to set Honeytail config if present (in hub)
        base_supervisor = os.path.join(client_root_dir, build_args['supervisor_file'])
        final_supervisor = os.path.join(client_root_dir, docker_args['SUPERVISOR_CONFIG'])

        with open(base_supervisor, 'rt') as source:
            with open(final_supervisor, 'wt') as dest:
                supervisor_data = source.read()
                context = base_data['container']['context']
                if context == "hub":
                    honeycomb_block = f"""\n
[program:honeytail]
command=/usr/bin/honeytail -c /etc/honeytail/honeytail.conf --file=/mnt/gigantum/.labmanager/logs/labmanager.log --parser=json --writekey={docker_args["HONEYCOMB_WRITE_KEY"]} --dataset={build_args['honeycomb_dataset']}
autostart=true
autorestart=true
priority=10"""
                else:
                    honeycomb_block = ""
                dest.write(f"""{supervisor_data}\n\n{honeycomb_block}""")

        # Image Labels
        labels = {'com.gigantum.app': 'client',
                  'com.gigantum.revision': get_current_commit_hash(),
                  'com.gigantum.version': release_version,
                  'com.gigantum.maintainer.email': 'support@gigantum.com'}

        # Delete .pyc files in case dev tools used on something not ubuntu before building
        self._remove_pyc(os.path.join(client_root_dir, "packages"))

        # Delete mypy cache before building
        self._remove_mypy_cache(client_root_dir)

        # Build image
        dockerfile_path = os.path.join(client_root_dir, 'resources', 'docker', 'Dockerfile')
        print("\n\n*** Building Gigantum Client image `{}`, please wait...\n\n".format(self.image_name))

        if is_windows:
            # This is a relative path from the *build context* (which is Linux)
            dockerfile_path = os.path.relpath(dockerfile_path, client_root_dir).replace('\\', '/')

        build_lines = self.docker_client.api.build(path=client_root_dir, dockerfile=dockerfile_path, tag=named_image,
                                                   labels=labels, nocache=no_cache, pull=True, rm=True, decode=True,
                                                   buildargs=docker_args)
        for line in build_lines:
            print(next(iter(line.values())), end='')

        # Tag with `latest` for auto-detection of image on launch
        # TODO: Rename container to gigantum/client
        self.docker_client.api.tag(named_image, self.image_name, 'latest')

    def publish(self, image_tag: str = None) -> None:
        """Method to push image to the logged in image repository server (e.g hub.docker.com)

        Args:
            image_tag(str): full image tag to publish
        """
        # If no tag provided, use current repo hash
        if not image_tag:
            image_tag = self.get_image_tag()

        last_msg = ""
        for ln in self.docker_client.api.push(self.image_name, tag=image_tag, stream=True, decode=True):
            if 'status' in ln:
                if last_msg != ln.get('status'):
                    print(f"\n{ln.get('status')}", end='', flush=True)
                    last_msg = ln.get('status')
                else:
                    print(".", end='', flush=True)

            elif 'error' in ln:
                sys.stderr.write(f"\n{ln.get('error')}\n")
                sys.stderr.flush()
            else:
                print(ln)

        self.docker_client.images.push(self.image_name, tag='latest')

    def publish_edge(self, image_tag: str = None) -> None:
        """Method to push image to the logged in image repository server (e.g hub.docker.com)

        Args:
            image_tag(str): full image tag to publish
        """
        # If no tag provided, use current repo hash
        if not image_tag:
            image_tag = self.get_image_tag()

        # Re-tag current labmanager build as edge locally
        self.docker_client.images.get(f'{self.image_name}:latest').tag(f'{self.image_name}-edge:{image_tag}')
        self.docker_client.images.get(f'{self.image_name}-edge:{image_tag}').tag(f'{self.image_name}-edge:latest')

        last_msg = ""
        for ln in self.docker_client.api.push(f'{self.image_name}-edge', tag=image_tag, stream=True, decode=True):
            if 'status' in ln:
                if last_msg != ln.get('status'):
                    print(f"\n{ln.get('status')}", end='', flush=True)
                    last_msg = ln.get('status')
                else:
                    print(".", end='', flush=True)

            elif 'error' in ln:
                sys.stderr.write(f"\n{ln.get('error')}\n")
                sys.stderr.flush()
            else:
                print(ln)

        self.docker_client.images.push(f'{self.image_name}-edge', tag='latest')

    def cleanup(self, image_name) -> None:
        """Method to clean up old images

        Args:
            image_name(str): Name of the image to cleanup (e.g. `gigantum/labmanager`)
        """
        images = self.docker_client.images.list(image_name)

        cnt = 0
        for image in images:
            if any(['latest' in x for x in image.tags]):
                continue
            cnt += 1

        if cnt == 0:
            print(f" - No old {image_name} images to remove\n")
            return None

        if not ask_question(f"\nDo you want to remove {cnt} old {image_name} images?"):
            print(" - Prune operation cancelled\n")
            return None

        print(f"\nRemoving old {image_name} images:")
        for image in images:
            if image.tags:
                if any(['latest' in x for x in image.tags]):
                    continue
                print(f" - Removing {image.tags[0]}")
                try:
                    self.docker_client.images.remove(image.id, force=True)
                except APIError:
                    print(f"Error trying to remove image, skipping {image.id}")
