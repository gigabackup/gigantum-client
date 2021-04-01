from client_app.pages.login.log_in_page import AuthLogInPage
from client_app.pages.login.ldap_login_page import LdapLogInPage
from client_app.pages.login.internal_login_page import InternalLogInPage


class LoginFactory:
    """ A factory class that creates the LoginPage based on the login type provided"""

    def load_login_page(self, login_type, driver):
        if login_type == 'auth0':
            login_page = AuthLogInPage(driver)
        elif login_type == 'ldap':
            login_page = LdapLogInPage(driver)
        elif login_type == 'internal':
            login_page = InternalLogInPage(driver)
        else:
            raise Exception("Invalid login type")
        return login_page

