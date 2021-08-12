import os
from typing import Tuple, Optional, List
import redis
import subprocess
import shlex

from gtmcore.logging import LMLogger
logger = LMLogger.get_logger()


# This table is a simplified version of https://github.com/NVIDIA/nvidia-docker/wiki/CUDA
# To interpret this data, cuda version 10.0 requires driver > 410.58
# We simplify the logic so that ANY supported card will work with the version we require
# e.g., if two cards are supported with different minimum versions, we only support the highest minimum
# At time of edit, we have explicitly tested through version 430
# Note that we don't support CUDA 8, but we don't disable it (yet)
CUDA_DRIVER_VERSION_LOOKUP = {8: {0: (375, 51)},
                              9: {0: (384, 81),
                                  1: (387, 26),
                                  2: (396, 26)},
                              10: {0: (410, 58),
                                   1: (418, 39),
                                   2: (440, 33)},
                              11: {0: (450, 36),
                                   1: (450, 80),
                                   2: (450, 80)}}


def _parse_version_str(version: Optional[str]) -> Optional[Tuple[int, int]]:
    result = None
    if version:
        version_nums = version.strip().split('.')
        if len(version_nums) == 2 or len(version_nums) == 3:
            try:
                result = (int(version_nums[0]), int(version_nums[1]))
            except ValueError:
                # Split two values, but they aren't convertible to ints
                pass
    return result


def should_launch_with_cuda_support(cuda_version: Optional[str]) -> Tuple[bool, str]:
    """Method to test whether the host has NVIDIA drivers, the Project is CUDA enabled, and the two are compatible.

        Args:
            cuda_version(str): Version of CUDA in the Project container, e.g. 9.2, 10.0

        Returns:
            bool
    """
    host_driver_version = os.environ.get('NVIDIA_DRIVER_VERSION')
    host_driver_version_nums = _parse_version_str(host_driver_version)
    reason = "Host does not have NVIDIA drivers configured"
    launch_with_cuda = False
    if host_driver_version_nums:
        reason = "Project is not GPU enabled"
        if cuda_version:
            # host has NVIDIA drivers installed
            cuda_version_nums = _parse_version_str(cuda_version)
            reason = "Failed to parse required CUDA version from Project configuration"
            if cuda_version_nums:
                # project has properly configured CUDA requirement
                driver_lookup = CUDA_DRIVER_VERSION_LOOKUP.get(cuda_version_nums[0])
                reason = f"Project CUDA version ({cuda_version}) not supported"
                if driver_lookup:
                    # Provided major version is supported
                    min_driver = driver_lookup.get(cuda_version_nums[1])
                    reason = f"Project CUDA version ({cuda_version}) not supported"
                    if min_driver:
                        project_major = min_driver[0]
                        project_minor = min_driver[1]
                        host_major = host_driver_version_nums[0]
                        host_minor = host_driver_version_nums[1]
                        reason = f"Project CUDA version ({cuda_version}) is not compatible with host" \
                            f" driver version ({host_driver_version})"
                        if host_major > project_major or (host_major == project_major and host_minor >= project_minor):
                            launch_with_cuda = True
                            reason = f"Project CUDA version ({cuda_version}) is compatible with host" \
                                f" driver version ({host_driver_version})"

    return launch_with_cuda, reason


class GPUNotAvailable(Exception):
    pass


class GPUInventory:
    """Class to track available GPUs and manage reservations when launching Projects
    """
    # Redis cache settings
    REDIS_DB = 0
    GPUS_AVAILABLE_KEY = "$GPUS_AVAILABLE$"
    GPU_ASSIGNMENT_KEY = "$GPU_ASSIGNMENT$"

    def __init__(self) -> None:
        self._redis_client: Optional[redis.Redis] = None

    def _get_redis_client(self) -> redis.Redis:
        """Method to get a redis client

        Returns:
            redis.Redis
        """
        if not self._redis_client:
            self._redis_client = redis.Redis(db=self.REDIS_DB, decode_responses=True)

        return self._redis_client

    def initialize(self, num_gpus: Optional[int] = None) -> None:
        """Populate the queue with the number of GPUs on the host

        Returns:
            None
        """
        client = self._get_redis_client()
        if not num_gpus:
            num_gpus = self._num_gpus()
        logger.info(f"{num_gpus} GPUs detected during initialization.")
        for idx in range(num_gpus):
            client.rpush(self.GPUS_AVAILABLE_KEY, idx)

    def _num_gpus(self) -> int:
        """Get the number of GPUs available on the host via the env var `NVIDIA_NUM_GPUS`, which is set by the CLI

        Returns:
            number of GPUs
        """
        num_gpus_str = os.environ.get('NVIDIA_NUM_GPUS')
        num_gpus = 0
        if num_gpus_str:
            num_gpus = int(num_gpus_str)
        return num_gpus

    def _active_users(self) -> List:
        """Get a list of usernames for users who have GPU reservations

        Returns:
            list of usernames
        """
        client = self._get_redis_client()
        reservations = client.hkeys(self.GPU_ASSIGNMENT_KEY)
        users = list()
        for r in reservations:
            username, _, _ = r.split('&')
            if username not in users:
                users.append(username)

        return users

    def reserve(self, username: str, owner: str, project_name: str) -> int:
        """Reserve a GPU (if available) and get its index

        Args:
            username: username for user who is launching a Project with a GPU
            owner: Owner of the Project being launched with the GPU
            project_name: Name of the Project being launch with the GPU

        Returns:
            index for the GPU that is now reserved for the specified user/owner/project combo
        """
        client = self._get_redis_client()
        available_idx = client.lpop(self.GPUS_AVAILABLE_KEY)
        if available_idx:
            client.hset(self.GPU_ASSIGNMENT_KEY, f"{username}&{owner}&{project_name}", available_idx)
            return int(available_idx)
        else:
            user_str = ", ".join(self._active_users())
            raise GPUNotAvailable(f"All available GPUs are currently in use. Stop a running Project and try again."
                                  f" Users with active GPU reservations: {user_str}")

    def release(self, username: str, owner: str, project_name: str) -> None:
        """Release a reserved GPU back to the pool

        Args:
            username: username for user who is stopping a Project that had been launched with a GPU
            owner: Owner of the Project that had been launched with a GPU
            project_name: Name of the Project that had been launched with a GPU

        Returns:
            None
        """
        client = self._get_redis_client()
        project_id = f"{username}&{owner}&{project_name}"
        gpu_idx = client.hget(self.GPU_ASSIGNMENT_KEY, project_id)
        if gpu_idx:
            client.rpush(self.GPUS_AVAILABLE_KEY, gpu_idx)
            client.hdel(self.GPU_ASSIGNMENT_KEY, project_id)
