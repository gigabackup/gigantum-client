import flask
import requests
from lmsrvcore.auth.identity import get_identity_manager_instance, AuthenticationError, tokens_from_headers
from gtmcore.logging import LMLogger
from gtmcore.configuration import Configuration

logger = LMLogger.get_logger()


def _is_ssl_issue(jwks_url: str) -> bool:
    """Helper method to verify if auth failed because of an ssl issue looking up the jwks

    Args:
        jwks_url: url to the jwks endpoint

    Returns:
        true if it is an ssl error, false if anything else happens (success or any other failure)
    """
    result = False
    try:
        requests.get(jwks_url)
    except requests.exceptions.SSLError:
        result = True
    except:
        pass

    return result


class AuthorizationMiddleware(object):
    """Middleware to enforce authentication requirements, parse JWTs, and switch server configuration.

    Note: info.context.is_authenticated attribute is used to ensure that an attempt to validate tokens
    is only run once per request. If this attribute exists in info.context, the parsing and validation code is skipped.

    """
    def resolve(self, next, root, info, **args):
        identity_mgr = get_identity_manager_instance()

        # If the `is_authenticated` field does not exist in the request context, process the headers
        if not hasattr(info.context, "is_authenticated"):

            # Change the server configuration if requested
            if "GTM-SERVER-ID" in info.context.headers:
                logger.info(f"Processing change server request for server id: {info.context.headers['GTM-SERVER-ID']}")
                config: Configuration = flask.current_app.config['LABMGR_CONFIG']
                current_config = config.get_server_configuration()

                # Force JWKS reload
                # This will be improved in #1433, as right now every request will load the jwk from disk
                identity_mgr.rsa_key = None

                try:
                    config.set_current_server(info.context.headers['GTM-SERVER-ID'])
                except Exception as err:
                    logger.exception(f"Failed to switch server configuration to server id"
                                     f" `{info.context.headers['GTM-SERVER-ID']}`")
                    # Roll back to previous server configuration
                    config.set_current_server(current_config.id)
                    logger.warning(f"Successfully rolled back server id to `{current_config.id}`")

            # Parse tokens
            access_token, id_token = tokens_from_headers(info.context.headers)

            # Save token to the request context for future use (e.g. look up a user's profile information if needed)
            flask.g.access_token = access_token
            flask.g.id_token = id_token

            # Check if you are authenticated, raising an AuthenticationError if you are not.
            if identity_mgr.is_authenticated(access_token, id_token):
                # We store the result of token validation in the request context so all resolvers don't need to
                # repeat this process for no reason.
                info.context.is_authenticated = True
            else:
                info.context.is_authenticated = False
                config: Configuration = flask.current_app.config['LABMGR_CONFIG']
                auth_config = config.get_auth_configuration()
                if _is_ssl_issue(auth_config.public_key_url):
                    raise AuthenticationError(
                        "SSL verification failed during JWKS fetch. Have you configured all of the "
                        "required certificates to use this server?", 401)
                raise AuthenticationError("User not authenticated", 401)

        if info.context.is_authenticated is False:
            raise AuthenticationError("User not authenticated", 401)

        return next(root, info, **args)
