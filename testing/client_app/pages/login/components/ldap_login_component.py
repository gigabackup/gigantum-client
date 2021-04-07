from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from client_app.pages.project_listing.project_listing_page import ProjectListingPage


class LdapLogInComponent(BaseComponent):
    """Represents login component of ldap login page.

    Holds a set of all locators within the user login frame on the login page of
    ldap server as an entity. Handles events and test functions of locators
    in this entity.
    """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(LdapLogInComponent, self).__init__(driver, component_data)
        self.title_login = self.get_locator(LocatorType.XPath, "//h2[@class='theme-heading']")

    def get_log_in_title(self) -> str:
        """Returns the title of login window."""
        return self.title_login.get_text()

    def login(self, user_name: str, password: str) -> ProjectListingPage:
        """Performs log-in functionality.

        Args:
            user_name:
                Name of the user who wants to login to the application.
            password:
                Password assigned for the current user.
        """
        txt_user_name = self.get_locator(LocatorType.XPath, "//input[@placeholder='email address']")
        txt_password = self.get_locator(LocatorType.XPath, "//input[@placeholder='password']")
        btn_login = self.get_locator(LocatorType.XPath, "//button[@id='submit-login']")
        txt_user_name.set_text(user_name)
        txt_password.set_text(password)
        btn_login.click()
        return ProjectListingPage(self.driver)

    def check_login_page_title(self) -> bool:
        """Check the login page title"""
        if self.title_login is not None:
            if self.title_login.get_text() == 'Log in to Your Account':
                return True
        return False

