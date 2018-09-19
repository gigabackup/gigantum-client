# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import platform

import docker

from gtm.common.dockerutil import dockerize_windows_path
from gtm.common.dockervolume import DockerVolume


class LabManagerRunner(object):
    """Class to manage the launch (or termination) of a labbook container.
    """

    def __init__(self, image_name: str, container_name: str, show_output: bool=False):
        self.docker_client = docker.from_env()
        self.image_name = image_name
        self.container_name = container_name
        self.docker_image = self.docker_client.images.get(image_name)
        self.show_output = show_output

        if not self.docker_image:
            raise ValueError("Image name `{}' does not exist.".format(image_name))

    @property
    def is_running(self):
        """Return True if a container by given name exists with `docker ps -a`. """
        return any([container.name == self.container_name for container in self.docker_client.containers.list()])

    def stop(self, cleanup: bool=True):
        """Stop the docker container by this name. """

        if not self.is_running:
            raise ValueError("Cannot stop container that is not running.")
        else:
            containers = list(filter(lambda c: c.name == self.container_name, self.docker_client.containers.list()))
            assert len(containers) == 1
            containers[0].stop()
            if cleanup:
                self.docker_client.containers.prune()

    def launch(self):
        """Launch the docker container. """
        working_dir = os.path.join(os.path.expanduser("~"), "gigantum")
        port_mapping = {'10000/tcp': 10000,
                        '10001/tcp': 10001,
                        '10002/tcp': 10002}

        # Make sure the container-container share volume exists
        share_volume = DockerVolume("labmanager_share_vol")
        if not share_volume.exists():
            share_volume.create()

        volume_mapping = {'labmanager_share_vol': {'bind': '/mnt/share', 'mode': 'rw'}}
        volume_mapping['/var/run/docker.sock'] = {'bind': '/var/run/docker.sock', 'mode': 'rw'}

        if platform.system() == 'Windows':
            # HOST_WORK_DIR will be used to mount inside labbook.
            environment_mapping = {'HOST_WORK_DIR': dockerize_windows_path(working_dir)}
            environment_mapping['WINDOWS_HOST'] = 1
            # Windows does not support cached, but this is silently ignored (as of late Jan 2018)
            # We convert \ to /
            volume_mapping[dockerize_windows_path(working_dir)] = {'bind': '/mnt/gigantum', 'mode': 'cached'}
        else:
            environment_mapping = {'HOST_WORK_DIR': working_dir}
            environment_mapping['LOCAL_USER_ID'] = os.getuid()
            volume_mapping[working_dir] = {'bind': '/mnt/gigantum', 'mode': 'cached'}

        self.docker_client.containers.run(image=self.docker_image,
                                          detach=True,
                                          name=self.container_name,
                                          init=True,
                                          ports=port_mapping,
                                          volumes=volume_mapping,
                                          environment=environment_mapping)
