import pytest
import responses

from gtmcore.workflows.gitlab import GitLabManager, ProjectPermissions, GitLabException
from gtmcore.fixtures import mock_config_file


@pytest.fixture()
def gitlab_mngr_fixture(mock_config_file):
    """A pytest fixture that returns a GitLabRepositoryManager instance"""
    yield GitLabManager("https://test.repo.gigantum.com/",
                        "https://test.gigantum.com/api/v1/", "fakeaccesstoken", "fakeidtoken")


@pytest.fixture()
def two_gitlab_mngr_fixture():
    """A pytest fixture that returns a GitLabRepositoryManager instance"""
    yield GitLabManager("https://test.repo.gigantum.com/", "https://test.gigantum.com/api/v1/",
                        "fakeaccesstoken", "fakeidtoken"), \
          GitLabManager("https://test.repo.gigantum.com/", "https://test.gigantum.com/api/v1/",
                        "fakeaccesstoken", "fakeidtoken")


@pytest.fixture()
def property_mocks_fixture():
    """A pytest fixture that returns a GitLabRepositoryManager instance"""
    responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)
    responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook',
                  json=[{
                          "id": 26,
                          "description": "",
                        }],
                  status=200)
    yield


class TestGitLabManager(object):
    @responses.activate
    def test_repo_token(self, gitlab_mngr_fixture):
        """test the repo_token property"""
        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)

        assert gitlab_mngr_fixture._gitlab_token is None

        # Get token
        token = gitlab_mngr_fixture._repo_token()
        assert token == 'afaketoken'
        assert gitlab_mngr_fixture._gitlab_token == 'afaketoken'

        # Assert token is returned and set on second call and does not make a request
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'NOTTHERIGHTTOKEN'}}}, status=500)
        assert token == gitlab_mngr_fixture._repo_token()
        assert token == 'afaketoken'

    @responses.activate
    def test_repo_token_error(self, gitlab_mngr_fixture):
        """test the repo_token property"""
        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'NOTTHERIGHTTOKEN'}}}, status=500)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)

        # Make sure error is raised when getting the key fails and returns !=200
        with pytest.raises(GitLabException):
            _ = gitlab_mngr_fixture._repo_token()

    def test_repository_id(self):
        """test the repository_id property"""
        assert GitLabManager.get_repository_id("tester", "test-lb-1") == "tester%2Ftest-lb-1"

    @responses.activate
    def test_exists_true(self, property_mocks_fixture, gitlab_mngr_fixture):
        """test the exists method for a repo that should exist"""
        assert gitlab_mngr_fixture.repository_exists("testuser", "test-labbook") is True

    @responses.activate
    def test_exists_wrong_content_type(self, property_mocks_fixture, gitlab_mngr_fixture):
        """test the exists method for a repo that should exist"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fbackup-in-progress',
                      content_type="text/plain",
                      status=200)
        assert gitlab_mngr_fixture.repository_exists("testuser", "backup-in-progress") is False

    @responses.activate
    def test_exists_false(self, gitlab_mngr_fixture):
        """test the exists method for a repo that should not exist"""
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fderp',
                      json=[{
                                "message": "404 Project Not Found"
                            }],
                      status=404)

        assert gitlab_mngr_fixture.repository_exists("testuser", "derp") is False

    @responses.activate
    def test_create(self, gitlab_mngr_fixture, property_mocks_fixture):
        """test the create method"""
        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.repo.gigantum.com/api/v4/projects',
                      json={
                              "id": 27,
                              "description": "",
                            },
                      status=201)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                                "message": "404 Project Not Found"
                            }],
                      status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)

        gitlab_mngr_fixture.create_labbook("testuser", "new-labbook", visibility="private")

        assert gitlab_mngr_fixture.repository_exists("testuser", "new-labbook") is True

    @responses.activate
    def test_create_errors(self, gitlab_mngr_fixture, property_mocks_fixture):
        """test the create method"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)

        # Should fail because the repo "already exists"
        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.create_labbook("testuser", "test-labbook", visibility="private")

        # Should fail because the call to gitlab failed
        responses.add(responses.POST, 'https://test.repo.gigantum.com/api/v4/projects',
                      json={
                              "id": 27,
                              "description": "",
                            },
                      status=400)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)
        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.create_labbook("testuser", "test-labbook", visibility="private")

    @responses.activate
    def test_set_visibility(self, gitlab_mngr_fixture, property_mocks_fixture):
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json={
                          "id": 27,
                          "description": "",
                      },
                      status=200)
        responses.add(responses.PUT, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      status=200)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json={
                          "id": 27,
                          "description": "",
                          "visibility": "public"
                      },
                      status=200)

        gitlab_mngr_fixture.set_visibility("testuser", "new-labbook", "public")

    @responses.activate
    def test_set_visibility_does_not_exist(self, gitlab_mngr_fixture, property_mocks_fixture):
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      content_type="text/plain",
                      status=200)

        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.set_visibility("testuser", "new-labbook", "public")

    @responses.activate
    def test_get_collaborators(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the get_collaborators method"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=1&per_page=20',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Jane Doe",
                                    "username": "janed",
                                    "access_level": ProjectPermissions.OWNER.value,
                                    "expires_at": None
                                },
                                {
                                    "id": 30,
                                    "name": "John Doeski",
                                    "username": "jd",
                                    "access_level": ProjectPermissions.READ_ONLY.value,
                                    "expires_at": None
                                }
                            ],
                      status=200)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=1&per_page=20',
                      status=400)

        collaborators = gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")

        assert len(collaborators) == 2
        assert collaborators[0] == (29, 'janed', ProjectPermissions.OWNER)
        assert collaborators[1] == (30, 'jd', ProjectPermissions.READ_ONLY)

        # Verify it fails on error to gitlab (should get second mock on second call)
        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")

    @responses.activate
    def test_add_collaborator(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the add_collaborator method"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.POST, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members',
                      json={
                                "id": 100,
                                "name": "New Person",
                                "username": "person100",
                                "state": "active",
                            },
                      status=201)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=1&per_page=20',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Jane Doe",
                                    "username": "janed",
                                    "access_level": 40,
                                    "expires_at": None
                                },
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "access_level": 30,
                                    "expires_at": None
                                }
                            ],
                      status=200)

        gitlab_mngr_fixture.add_collaborator("testuser", "test-labbook", "person100",
                                             ProjectPermissions.READ_WRITE)

        collaborators = gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")
        assert len(collaborators) == 2
        assert collaborators[0] == (29, 'janed', ProjectPermissions.OWNER)
        assert collaborators[1] == (100, 'person100', ProjectPermissions.READ_WRITE)

    @responses.activate
    def test_add_collaborator_errors(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the add_collaborator method exception handling"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=400)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=201)
        responses.add(responses.POST, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                      'page=1&per_page=20',
                      json={
                                "id": 100,
                                "name": "New Person",
                                "username": "person100",
                                "state": "active",
                            },
                      status=400)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)

        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.add_collaborator("testuser", "test-labbook", "person100", ProjectPermissions.OWNER)

        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.add_collaborator("testuser", "test-labbook", "person100", ProjectPermissions.READ_ONLY)

    @responses.activate
    def test_delete_collaborator(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the delete_collaborator method"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.DELETE, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members/100',
                      status=204)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=1&per_page=20',
                      json=[
                                {
                                    "id": 29,
                                    "name": "Jane Doe",
                                    "username": "janed",
                                    "access_level": 40,
                                    "expires_at": None
                                }
                            ],
                      status=200)

        gitlab_mngr_fixture.delete_collaborator("testuser", "test-labbook", 'person100')
        collaborators = gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")
        assert len(collaborators) == 1
        assert collaborators[0] == (29, 'janed', ProjectPermissions.OWNER)

    @responses.activate
    def test_delete_collaborator_error(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the delete_collaborator method exception handling"""
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.DELETE, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members/100',
                      status=204)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/users?username=person100',
                      json=[
                                {
                                    "id": 100,
                                    "name": "New Person",
                                    "username": "person100",
                                    "state": "active",
                                }
                            ],
                      status=200)
        responses.add(responses.DELETE, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members/100',
                      status=400)

        gitlab_mngr_fixture.delete_collaborator("testuser", "test-labbook", 'person100')
        with pytest.raises(ValueError):
            gitlab_mngr_fixture.delete_collaborator("testuser", "test-labbook", 'person100')

    @responses.activate
    def test_get_collaborators_pagination(self, gitlab_mngr_fixture, property_mocks_fixture):
        """Test the get_collaborators method and required pagination"""
        data1 = [{"id": 1,
                  "name": "Jane Doe",
                  "username": "janed",
                  "access_level": ProjectPermissions.OWNER.value,
                  "expires_at": None}]
        for idx in range(2, 21):
            data1.append({"id": idx,
                          "name": f"User {idx}",
                          "username": f"user{idx}",
                          "access_level": ProjectPermissions.READ_ONLY.value,
                          "expires_at": None})
        data2 = list()
        for idx in range(21, 25):
            data2.append({"id": idx,
                          "name": f"User {idx}",
                          "username": f"user{idx}",
                          "access_level": ProjectPermissions.READ_ONLY.value,
                          "expires_at": None})

        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=1&per_page=20',
                      json=data1,
                      status=200)

        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook/members?'
                                     'page=2&per_page=20',
                      json=data2,
                      status=200)

        collaborators = gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")

        assert len(collaborators) == 24
        assert collaborators[0] == (1, 'janed', ProjectPermissions.OWNER)
        assert collaborators[1] == (2, 'user2', ProjectPermissions.READ_ONLY)
        assert collaborators[23] == (24, 'user24', ProjectPermissions.READ_ONLY)

    @responses.activate
    def test_error_on_missing_repo(self, gitlab_mngr_fixture):
        """Test the exception handling on a repo when it doesn't exist"""
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Ftest-labbook',
                      json=[{
                                "message": "404 Project Not Found"
                            }],
                      status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)

        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.get_collaborators("testuser", "test-labbook")
        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.add_collaborator("testuser", "test-labbook", "test", ProjectPermissions.READ_ONLY)
        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.delete_collaborator("testuser", "test-labbook", "test")

    @responses.activate
    def test_configure_git_credentials(self, gitlab_mngr_fixture):
        """test the configure_git_credentials method"""
        host = "https://test.gigantum.io/"
        username = "testuser"

        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)

        # Check that creds are empty
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token is None

        # Set creds
        gitlab_mngr_fixture.configure_git_credentials(host, username)

        # Check that creds are configured
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token == "afaketoken"

        # Set creds
        gitlab_mngr_fixture.clear_git_credentials(host, username)

        # Check that creds are configured
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token is None

    @responses.activate
    def test_configure_git_credentials_multitenant(self, two_gitlab_mngr_fixture):
        """test the configure_git_credentials method with multiple users

        Two gitlab manager instances are used because in practice, each request context will have it's own instance.
        The gitlab API token is stored as a class attribute once fetched, to reduce API calls, so we have to create
        two intances for this test to work.

        """
        host = "https://test.gigantum.io"
        username1 = "testuser1"
        username2 = "testuser2"

        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken1'}}}, status=200)
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken2'}}}, status=200)

        glm1, glm2 = two_gitlab_mngr_fixture

        # Check that creds are empty
        token1 = glm1._check_if_git_credentials_configured(host, username1)
        assert token1 is None
        token2 = glm2._check_if_git_credentials_configured(host, username2)
        assert token2 is None

        # Set creds
        glm1.configure_git_credentials(host, username1)

        # Check that creds are configured
        token1 = glm1._check_if_git_credentials_configured(host, username1)
        assert token1 == "afaketoken1"
        token2 = glm2._check_if_git_credentials_configured(host, username2)
        assert token2 is None

        # Set creds
        glm2.configure_git_credentials(host, username2)
        token1 = glm1._check_if_git_credentials_configured(host, username1)
        assert token1 == "afaketoken1"
        token2 = glm2._check_if_git_credentials_configured(host, username2)
        assert token2 == "afaketoken2"

        glm2.clear_git_credentials(host, username2)

        token1 = glm1._check_if_git_credentials_configured(host, username1)
        assert token1 == "afaketoken1"
        token2 = glm2._check_if_git_credentials_configured(host, username2)
        assert token2 is None

        glm1.clear_git_credentials(host, username1)

        token1 = glm1._check_if_git_credentials_configured(host, username1)
        assert token1 is None
        token2 = glm2._check_if_git_credentials_configured(host, username2)
        assert token2 is None

    @responses.activate
    def test_remove_git_credentials(self, gitlab_mngr_fixture):
        """test the remove git credential method, particularly when nothing to remove"""
        host = "https://test.gigantum.io"
        username = "testuser"

        # Setup responses mock for this test
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'additionalCredentials': {'gitServiceToken': 'afaketoken'}}}, status=200)

        # Remove creds before set
        gitlab_mngr_fixture.clear_git_credentials(host, username)
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token is None

        # Set creds
        gitlab_mngr_fixture.configure_git_credentials(host, username)

        # Check that creds are configured
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token == "afaketoken"

        # Remove creds
        gitlab_mngr_fixture.clear_git_credentials(host, username)

        # Check that creds are configured
        token = gitlab_mngr_fixture._check_if_git_credentials_configured(host, username)
        assert token is None

        # Remove creds again after already removed.
        gitlab_mngr_fixture.clear_git_credentials(host, username)

    @responses.activate
    def test_delete(self, gitlab_mngr_fixture, property_mocks_fixture):
        """test the create method"""
        # Setup responses mock for this test
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                              "id": 27,
                              "description": "",
                            }],
                      status=200)
        responses.add(responses.DELETE, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json={
                                "message": "202 Accepted"
                            },
                      status=202)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                                "message": "404 Project Not Found"
                            }],
                      status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/api/v4/projects/testuser%2Fnew-labbook',
                      json=[{
                                "message": "404 Project Not Found"
                            }],
                      status=404)
        responses.add(responses.GET, 'https://test.repo.gigantum.com/backup', status=404)

        assert gitlab_mngr_fixture.repository_exists("testuser", "new-labbook") is True

        gitlab_mngr_fixture.remove_repository("testuser", "new-labbook")

        assert gitlab_mngr_fixture.repository_exists("testuser", "new-labbook") is False

        with pytest.raises(GitLabException):
            gitlab_mngr_fixture.remove_repository("testuser", "new-labbook")
