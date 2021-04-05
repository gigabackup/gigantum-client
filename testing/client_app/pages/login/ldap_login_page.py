from framework.base.page_base import BasePage
from framework.factory.models_enums.page_config import PageConfig
from framework.factory.models_enums.page_config import ComponentModel
from client_app.pages.login.components.ldap_login_component import LdapLogInComponent
from client_app.pages.login.login_interface import Login
from client_app.pages.project_listing.project_listing_page import ProjectListingPage


class LdapLogInPage(BasePage, Login):
    """Represents the login page of ldap server.

    Holds the locators on the login page of ldap server. The locators can be
    presented in its corresponding component or directly on the page. Test functions can
    use these objects for all activities and validations and can avoid those in the
    test functions.
    """

    def __init__(self, driver) -> None:
        page_config = PageConfig()
        super(LdapLogInPage, self).__init__(driver, page_config)
        self._log_in_component_model = ComponentModel()
        self._sign_up_component_model = ComponentModel()
        self._sign_up_component = None
        self._log_in_component = None

    @property
    def ldap_log_in_component(self) -> LdapLogInComponent:
        """Log-in component."""
        if self._log_in_component is None:
            self._log_in_component = LdapLogInComponent(self.driver, self._log_in_component_model)
        return self._log_in_component

    def login(self, user_name: str, password: str) -> ProjectListingPage:
        """Performs log-in functionality.

        Args:
            user_name:
                Name of the user who wants to login to the application.
            password:
                Password assigned for the current user.

        Returns:
            Instance of project list page.
        """
        self.ldap_log_in_component.login(user_name, password)
        return ProjectListingPage(self.driver)

    def check_login_page_title(self):
        """Check login page title

        Returns: returns the result of title checking

        """
        return self.ldap_log_in_component.check_login_page_title()

