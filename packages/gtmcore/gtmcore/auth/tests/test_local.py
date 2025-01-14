import pytest
import os
import responses
import requests
import time
import mock
from typing import Optional
import jose
import json

from gtmcore.configuration import Configuration
from gtmcore.fixtures.auth import mock_config_file_with_auth, mock_config_file_with_auth_first_login
from gtmcore.auth.identity import get_identity_manager_class, AuthenticationError
from gtmcore.auth.local import LocalIdentityManager
from gtmcore.auth import User


def mock_import(archive_path: str, username: str, owner: str, base_filename: Optional[str] = None,
                remove_source: bool = True):
    if not username:
        username = "johndoe"
    if not base_filename:
        base_filename = "my-first-project"

    config = Configuration()
    lb_dir = os.path.join(config.get_user_storage_dir(), username, owner, "labbooks", base_filename)
    os.makedirs(lb_dir, exist_ok=True)
    assert os.path.exists(lb_dir)

    class FakeLB:
        @property
        def root_dir(self):
            return lb_dir

        @property
        def name(self):
            return base_filename

    return FakeLB()


def mock_jwt_claims(data):
    return json.loads(data)


def mock_jwt_validate(self, token, client_id, limited_validation):
    return {"email": "test@gigantum.com",
            "nickname": "testuser",
            "given_name": "test",
            "family_name": "user"}


def clean_local_cache(mgr):
    """Simple helper to cleanup the local cached id since reusing the working dir to reduce API calls to Auth0"""
    id_file = os.path.join(mgr.auth_dir, 'cached_id_jwt')
    if os.path.exists(id_file):
        os.remove(id_file)


class TestIdentityLocal(object):
    def test_load_user_no_user(self, mock_config_file_with_auth):
        """test getting an identity manager"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Load User
        assert mgr._load_user(None) is None

        clean_local_cache(mgr)

    def test_save_load_user(self, mock_config_file_with_auth):
        """test getting an identity manager"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Save User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
        mgr._safe_cached_id_access(mock_config_file_with_auth[1]['id_token'])
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

        # Load User
        u2 = mgr._load_user(None)
        assert type(u2) == User

        assert "johndoe" == u2.username
        assert "john.doe@gmail.com" == u2.email
        assert "John" == u2.given_name
        assert "Doe" == u2.family_name

        clean_local_cache(mgr)

    def test_load_user_refresh(self, mock_config_file_with_auth):
        """handling a new token for the same user"""
        config = Configuration()

        with mock.patch.object(jose.jwt, 'get_unverified_claims', lambda x: mock_jwt_claims(x)):
            with mock.patch.object(LocalIdentityManager, 'validate_jwt_token', mock_jwt_validate):

                mgr = get_identity_manager_class(config)(config)
                assert type(mgr) == LocalIdentityManager

                # Save User
                assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
                mgr._safe_cached_id_access(json.dumps({'nickname': 'testuser', 'dummy': '1'}))
                assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

                with open(os.path.join(mgr.auth_dir, 'cached_id_jwt'), 'rt') as cf:
                    data = json.loads(json.load(cf))
                assert data['dummy'] == '1'

                # Load User
                u2 = mgr._load_user(json.dumps({'nickname': 'testuser', 'dummy': '2'}))
                assert type(u2) == User

                assert "testuser" == u2.username
                assert "test@gigantum.com" == u2.email
                assert "test" == u2.given_name
                assert "user" == u2.family_name

                with open(os.path.join(mgr.auth_dir, 'cached_id_jwt'), 'rt') as cf:
                    data = json.loads(json.load(cf))
                assert data['dummy'] == '2'

                clean_local_cache(mgr)

    def test_load_user_mismatch(self, mock_config_file_with_auth):
        """handling a new token for the same user"""
        config = Configuration()

        with mock.patch.object(jose.jwt, 'get_unverified_claims', lambda x: mock_jwt_claims(x)):
            with mock.patch.object(LocalIdentityManager, 'validate_jwt_token', mock_jwt_validate):

                mgr = get_identity_manager_class(config)(config)
                assert type(mgr) == LocalIdentityManager

                # Save User
                assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
                mgr._safe_cached_id_access(json.dumps({'nickname': 'olduser', 'dummy': '1'}))
                assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

                # Load User
                u2 = mgr._load_user(json.dumps({'nickname': 'testuser', 'dummy': '1'}))
                assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False

        clean_local_cache(mgr)

    def test_load_corrupt(self, mock_config_file_with_auth):
        """handling a corrupted cached id token"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        os.makedirs(mgr.auth_dir, exist_ok=True)
        with open(os.path.join(mgr.auth_dir, 'cached_id_jwt'), 'wt') as cf:
            cf.write('"sdfsd"df"')

        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

        # Load User
        with pytest.raises(json.decoder.JSONDecodeError):
            mgr._load_user(None)

        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False

        clean_local_cache(mgr)

    def test_logout_user(self, mock_config_file_with_auth):
        """test getting an identity manager"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Save User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
        mgr._safe_cached_id_access(mock_config_file_with_auth[1]['id_token'])
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True
        assert os.path.exists(os.path.join(mgr.auth_dir, 'test-gigantum-com-jwks.json')) is True

        # Load User
        mgr.logout()
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
        assert os.path.exists(os.path.join(mgr.auth_dir, 'test-gigantum-com-jwks.json')) is False
        assert mgr.user is None
        assert mgr.rsa_key is None
        assert mgr._load_user(None) is None

        clean_local_cache(mgr)

    def test_authenticate_user_exists_no_token(self, mock_config_file_with_auth):
        """test getting a user after stored locally already"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Save User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
        mgr._safe_cached_id_access(mock_config_file_with_auth[1]['id_token'])
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

        # Load User
        u2 = mgr.get_user_profile()
        assert type(u2) == User

        assert "johndoe" == u2.username
        assert "john.doe@gmail.com" == u2.email
        assert "John" == u2.given_name
        assert "Doe" == u2.family_name

        clean_local_cache(mgr)

    def test_authenticate_user_exists_token(self, mock_config_file_with_auth):
        """test getting a user after stored locally already"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Save User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is False
        mgr._safe_cached_id_access(mock_config_file_with_auth[1]['id_token'])
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True

        # Load User
        u2 = mgr.get_user_profile(mock_config_file_with_auth[1]['access_token'],
                                  mock_config_file_with_auth[1]['id_token'])
        assert type(u2) == User

        assert "johndoe" == u2.username
        assert "john.doe@gmail.com" == u2.email
        assert "John" == u2.given_name
        assert "Doe" == u2.family_name

        clean_local_cache(mgr)

    def test_get_profile_attribute(self, mock_config_file_with_auth):
        """test getting profile attributes safely from the profile dictionary"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)

        profile_data = {"username": "",
                        "email": "test@test.com"}

        assert mgr._get_profile_attribute(profile_data, "email") == "test@test.com"
        assert mgr._get_profile_attribute(profile_data, "email", False) == "test@test.com"

        assert mgr._get_profile_attribute(profile_data, "username", False) is None

        with pytest.raises(AuthenticationError):
            mgr._get_profile_attribute(profile_data, "username")
        with pytest.raises(AuthenticationError):
            mgr._get_profile_attribute(profile_data, "username", True)

        with pytest.raises(AuthenticationError):
            mgr._get_profile_attribute(profile_data, "first_name")

        assert mgr._get_profile_attribute(profile_data, "first_name", False) is None

        clean_local_cache(mgr)

    def test_is_session_valid(self, mock_config_file_with_auth):
        """test check for valid session"""
        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Invalid with no token
        assert mgr.is_token_valid() is False
        assert mgr.is_token_valid(None) is False
        assert mgr.is_token_valid("asdfasdfasdf") is False

        assert mgr.is_token_valid(mock_config_file_with_auth[1]['access_token']) is True
        assert mgr.rsa_key is not None

        clean_local_cache(mgr)

    @responses.activate
    def test_is_authenticated_token(self, mock_config_file_with_auth):
        """test checking if the user is authenticated via a token"""
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'synchronizeUserAccount': {'gitUserId': "123"}}},
                      status=200)

        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Invalid with no token
        assert mgr.is_authenticated() is False
        assert mgr.is_authenticated(None) is False
        assert mgr.is_authenticated("asdfasdfa") is False
        assert mgr.is_authenticated("asdfasdfa", "asdfasdffdgfgh") is False

        assert mgr.is_authenticated(mock_config_file_with_auth[1]['access_token'],
                                    mock_config_file_with_auth[1]['id_token']) is True

        # Second access should load from disk and not need a token
        mgr2 = get_identity_manager_class(config)(config)
        assert mgr2.is_authenticated() is True
        assert mgr2.is_authenticated("asdfasdfa") is True  # An "expired" token will essentially do this

        # Double check logging out un-authenticates
        mgr2.logout()
        assert mgr.is_authenticated() is False
        assert mgr2.is_authenticated() is False

        clean_local_cache(mgr)

    @responses.activate
    def test_get_user_profile(self, mock_config_file_with_auth):
        """test getting a user profile from Auth0"""
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'synchronizeUserAccount': {'gitUserId': "123"}}},
                      status=200)
        responses.add_passthru('https://auth.gigantum.com/.well-known/jwks.json')

        config = Configuration()
        mgr = get_identity_manager_class(config)(config)
        assert type(mgr) == LocalIdentityManager

        # Load User
        with pytest.raises(AuthenticationError):
            # Should fail without a token
            mgr.get_user_profile()

        # Load User
        u = mgr.get_user_profile(mock_config_file_with_auth[1]['access_token'],
                                 mock_config_file_with_auth[1]['id_token'])
        assert type(u) == User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True
        assert u.username == "johndoe"
        assert u.email == "john.doe@gmail.com"
        assert u.given_name == "John"
        assert u.family_name == "Doe"

        # Seccond access should load from disk and not need a token
        mgr2 = get_identity_manager_class(config)(config)
        u2 = mgr2.get_user_profile()
        assert type(u) == User
        assert os.path.exists(os.path.join(mgr.auth_dir, 'cached_id_jwt')) is True
        assert u2.username == "johndoe"
        assert u2.email == "john.doe@gmail.com"
        assert u2.given_name == "John"
        assert u2.family_name == "Doe"

        # Double check logging out un-authenticates
        mgr2.logout()
        with pytest.raises(AuthenticationError):
            # Should fail without a token
            mgr.get_user_profile()
        with pytest.raises(AuthenticationError):
            # Should fail without a token
            mgr2.get_user_profile()

        clean_local_cache(mgr)

    def test_check_first_login_errors(self, mock_config_file_with_auth_first_login):
        """Test login, but the user already logged into this instance"""
        # fake the user already existing by creating the user directory
        config_instance, tokens, work_dir = mock_config_file_with_auth_first_login
        os.makedirs(os.path.join(config_instance.get_user_storage_dir(), "johndoe"))

        mgr = get_identity_manager_class(config_instance)(config_instance)

        with pytest.raises(ValueError):
            mgr._check_first_login("", "", "")

        with pytest.raises(ValueError):
            mgr._check_first_login("johndoe", "", "")

        with pytest.raises(ValueError):
            mgr._check_first_login("", "asdf", "")

        with pytest.raises(ValueError):
            mgr._check_first_login("", tokens['access_token'], "")

    def test_check_first_login_user_locally(self, mock_config_file_with_auth_first_login):
        """Test login, but the user already logged into this instance"""
        # fake the user already existing by creating the user directory
        config_instance, tokens, work_dir = mock_config_file_with_auth_first_login
        os.makedirs(os.path.join(config_instance.get_user_storage_dir(), "johndoe"))
        mgr = get_identity_manager_class(config_instance)(config_instance)

        mgr._check_first_login("johndoe", access_token=tokens['access_token'],
                               id_token=tokens['id_token'])

        # Should not import labbook - note we aren't mocking all the way to the workers
        time.sleep(5)
        assert os.path.exists(os.path.join(config_instance.get_user_storage_dir(), "johndoe", "johndoe", "labbooks",
                                           "my-first-project")) is False

    @mock.patch('gtmcore.workflows.ZipExporter.import_labbook', side_effect=mock_import)
    @responses.activate
    def test_check_first_login_no_user_locally_in_repo(self, mock_import, mock_config_file_with_auth_first_login):
        """Test login with the user in the repo already"""
        responses.add(responses.POST, 'https://test.gigantum.com/api/v1/',
                      json={'data': {'synchronizeUserAccount': {'gitUserId': 123}}}, status=200)

        config_instance, tokens, work_dir = mock_config_file_with_auth_first_login
        mgr = get_identity_manager_class(config_instance)(config_instance)

        mgr._check_first_login("johndoe", access_token=tokens['access_token'],
                               id_token=tokens['id_token'])

        # Should import labbook - note we aren't mocking all the way to the workers
        time.sleep(5)
        assert os.path.exists(os.path.join(config_instance.get_user_storage_dir(), "johndoe", "johndoe", "labbooks",
                                           "my-first-project")) is True

    def test_get_jwt_public_key(self, mock_config_file_with_auth):
        def mock_jwt_header(x):
            return {"alg": "RS256","typ": "JWT","kid": "NzkwQzEyMTNDRUMzQjI3RkQ2QkVEQ0M1ODBDNjExMjRGOUNCRDBBQg"}

        config_instance, tokens, work_dir = mock_config_file_with_auth

        # Remove jwks inserted in mock so it re-downloads for real.
        jkws_path = os.path.join(config_instance.app_workdir, '.labmanager', 'identity', 'test-gigantum-com-jwks.json')
        assert os.path.isfile(jkws_path) is True
        os.remove(jkws_path)
        assert os.path.isfile(jkws_path) is False

        mgr = get_identity_manager_class(config_instance)(config_instance)

        with mock.patch.object(jose.jwt, 'get_unverified_header', lambda x: mock_jwt_header(x)):
            jwk_data = mgr._get_jwt_public_key(tokens['id_token'])
            assert jwk_data['kid'] == "NzkwQzEyMTNDRUMzQjI3RkQ2QkVEQ0M1ODBDNjExMjRGOUNCRDBBQg"
            assert os.path.isfile(jkws_path) is True
