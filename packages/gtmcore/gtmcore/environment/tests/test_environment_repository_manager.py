import os
import pickle
from pathlib import Path
from subprocess import run

import pytest
from git import Repo

from gtmcore.environment import RepositoryManager
from gtmcore.fixtures import mock_config_file, mock_config_with_repo, \
    ENV_UNIT_TEST_BASE, ENV_UNIT_TEST_REPO, ENV_UNIT_TEST_REV
from gtmcore.fixtures.fixtures import _create_temp_work_dir
from gtmcore.environment.tests import ENV_SKIP_MSG, ENV_SKIP_TEST


@pytest.mark.skipif(ENV_SKIP_TEST, reason=ENV_SKIP_MSG)
class TestEnvironmentRepositoryManager(object):
    def test_clone_repositories_branch(self):
        """Test cloning a branch"""
        config_instance, _ = _create_temp_work_dir(override_dict={'environment':
                   {'repo_url': ["https://github.com/gigantum/base-images-testing.git@test-branch-DONOTDELETE"]}})

        # Run clone and index operation
        erm = RepositoryManager()
        erm.update_repositories()

        working_dir = config_instance.app_workdir
        assert os.path.exists(os.path.join(working_dir, ".labmanager")) is True
        assert os.path.exists(os.path.join(working_dir, ".labmanager", "environment_repositories")) is True
        assert os.path.exists(os.path.join(working_dir, ".labmanager", "environment_repositories",
                                           ENV_UNIT_TEST_REPO)) is True
        assert os.path.exists(os.path.join(working_dir, ".labmanager", "environment_repositories",
                                           ENV_UNIT_TEST_REPO, "README.md")) is True

        r = Repo(os.path.join(working_dir, ".labmanager", "environment_repositories", ENV_UNIT_TEST_REPO))
        assert r.active_branch.name == "test-branch-DONOTDELETE"

    def test_update_repositories(self, mock_config_with_repo):
        """Test building the index"""
        config_instance, _ = mock_config_with_repo

        working_dir = config_instance.app_workdir
        gigantum_path = Path(working_dir)
        base_repo = gigantum_path / ".labmanager" / "environment_repositories" / ENV_UNIT_TEST_REPO
        # Existence of the README file implies all intermediate directories exist
        assert (base_repo / "README.md").exists()
        # This will break if we change master, or if somehow we get some other HEAD that's not master
        assert run(['git', 'rev-parse', 'HEAD'], cwd=base_repo, capture_output=True).stdout.strip() == \
                b'dd217c054141c6ce9f1b28268a2673c63959c1f4'

        # If the repositories are already checked out, this triggers a different code-path
        erm = RepositoryManager()
        erm.update_repositories()

        assert run(['git', 'rev-parse', 'HEAD'], cwd=base_repo, capture_output=True).stdout.strip() == \
               b'dd217c054141c6ce9f1b28268a2673c63959c1f4'

    def test_index_repositories_base_image(self, mock_config_with_repo):
        """Test creating and accessing the detail version of the base image index"""
        # Verify index file contents
        erm = RepositoryManager()
        with open(os.path.join(erm.local_repo_directory, "base_index.pickle"), 'rb') as fh:
            data = pickle.load(fh)

        assert ENV_UNIT_TEST_REPO in data
        assert ENV_UNIT_TEST_BASE in data[ENV_UNIT_TEST_REPO]
        assert ENV_UNIT_TEST_REV in data[ENV_UNIT_TEST_REPO][ENV_UNIT_TEST_BASE]
        assert "image" in data[ENV_UNIT_TEST_REPO][ENV_UNIT_TEST_BASE][ENV_UNIT_TEST_REV]
        assert "server" in data[ENV_UNIT_TEST_REPO][ENV_UNIT_TEST_BASE][ENV_UNIT_TEST_REV]['image']
        assert "package_managers" in data[ENV_UNIT_TEST_REPO][ENV_UNIT_TEST_BASE][ENV_UNIT_TEST_REV]
        assert "repository" in data[ENV_UNIT_TEST_REPO][ENV_UNIT_TEST_BASE][ENV_UNIT_TEST_REV]

    def test_index_repositories_base_image_list(self, mock_config_with_repo):
        """Test accessing the list version of the base image index"""
        # Verify index file contents
        erm = RepositoryManager()
        with open(os.path.join(erm.local_repo_directory, "base_list_index.pickle"), 'rb') as fh:
            data = pickle.load(fh)

        assert len(data) >= 2
        assert any(n.get('id') == ENV_UNIT_TEST_BASE for n in data)
