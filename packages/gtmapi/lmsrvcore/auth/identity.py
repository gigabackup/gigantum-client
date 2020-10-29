from typing import Tuple, Optional
from gtmcore.auth.identity import AuthenticationError, IdentityManager
import flask
import base64


def get_identity_manager_instance() -> IdentityManager:
    """Method to retrieve the id manager from the flask application"""
    id_mgr: Optional[IdentityManager] = flask.g.get('ID_MGR', None)
    if not id_mgr:
        # Instantiate and Identity Manager class for this request
        id_mgr = flask.current_app.config["ID_MGR_CLS"](flask.current_app.config["LABMGR_CONFIG"])
        flask.g.ID_MGR = id_mgr
    return id_mgr


def tokens_from_headers(headers: dict) -> Tuple[Optional[str], Optional[str]]:
    """Method to retrieve the access and id tokens from the request headers, if available."""
    access_token = None
    id_token = None
    if "Authorization" in headers:
        try:
            _, access_token = headers['Authorization'].split("Bearer ")
        except ValueError:
            raise AuthenticationError("Could not parse JWT from Authorization Header. Should be `Bearer <token>`", 401)

    if "Identity" in headers:
        id_token = headers['Identity']

    return access_token, id_token


def tokens_from_request_context(tokens_required=False) -> Tuple[Optional[str], Optional[str]]:
    """Method to return tokens stored in the flask request context. If `tokens_required` is True, an AuthenticationError
    exception will be raised if tokens are not present.

    Args:
        tokens_required: boolean indicating if tokens must exist

    """
    access_token = flask.g.get('access_token', None)
    id_token = flask.g.get('id_token', None)

    if tokens_required:
        if not access_token or not id_token:
            raise AuthenticationError("This operation requires a valid session. Please log in.", 401)

    # If the access token is an anonymous token, set tokens to None so future requests and git operations
    # try to run without authentication.
    if access_token:
        parts = access_token.split('.')
        if len(parts) == 3:
            header = base64.urlsafe_b64decode(f"{parts[0]}{'=' * (len(parts[0]) % 4)}").decode()
            if "GIGANTUM-ANONYMOUS-USER" == header:
                access_token = None
                id_token = None

    return access_token, id_token
