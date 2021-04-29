import os
import tempfile
import time
from framework.base.component_base import BaseComponent
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from framework.factory.models_enums.constants_enums import LocatorType
from selenium.webdriver.common.keys import Keys


class PackageGridComponent(BaseComponent):
    """ Represents one of the components while viewing the package lists .

    Holds a set of all locators within grid for each project package as an entity. Helps in iterating through the
    package details in the grid Handles events and test functions of locators
    """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(PackageGridComponent, self).__init__(driver, component_data)
        self.package_body_title = self.get_locator(LocatorType.XPath, "//div[@data-selenium-id='PackageCard']"
                                                                      "/div[@data-selenium-id='PackageBody']")
        self.add_package_button = self.get_locator(LocatorType.XPath, "//div[@data-selenium-id='PackageCard']"
                                                                      "/button[contains(text(),'Add Package')]")

    def get_package_body_title(self) -> str:
        """ Locate the the text on package body

        Returns: returns the package body text as a string

        """
        return self.package_body_title.get_text()

    def click_add_package_button(self) -> bool:
        """Performs click action on add package button

        Returns: returns the result of click action

        """
        if self.add_package_button is not None and self.add_package_button.element_to_be_clickable():
            self.add_package_button.execute_script("arguments[0].click();")
            return True
        return False

    def verify_package_list(self, package_details_list: list) -> bool:
        """Verify all installed packages

        Args:
            package_details_list: Details of packages

        Returns: returns the comparison result

        """
        package_list = self.ui_element.find_elements_by_xpath("//div[@data-selenium-id='PackageRow']")
        if package_list is not None:
            # Iterate the page elements corresponding to package details
            agent = self.driver.capabilities['browserName']
            for index, package in enumerate(package_list):
                package_detail = package.text.split('\n')
                if agent.lower() in ['chrome', 'firefox']:
                    package_name, package_version = package_detail[1], package_detail[3]
                    # Compare package-details on page with the package-details from argument
                    if package_name != package_details_list[index].name or package_version != \
                            package_details_list[index].version:
                        return False
                elif agent.lower() == 'safari':
                    # Safari returns a single string with no delimiters so check in a less strict way
                    # by just seeing if the name and version are in the string
                    if package_details_list[index].name not in package_detail[0] or \
                            package_details_list[index].version not in package_detail[0]:
                        return False
        return True

    def check_package_update(self, package_name: str, check_string: str) -> bool:
        """Check for the package update

        Args:
            package_name: Name of the package
            check_string: String to compare

        Returns: returns the comparison result

        """
        package_list = self.ui_element.find_elements_by_xpath("//div[@data-selenium-id='PackageRow']")
        if package_list is not None:
            for package in package_list:
                package_title = package.text.split('\n')[1]
                if package_title == package_name:
                    update_text = package.find_element_by_xpath(".//div[@data-selenium-id='PackageActions']/button[1]")
                    if update_text.getAttribute("data-tooltip") == check_string:
                        return True
        return False

    def click_update_package_button(self) -> bool:
        """Performs click action on Update Package button

        Returns: returns the result of click action

        """
        update_button = self.get_locator(LocatorType.XPath, "//button[@data-tooltip='Update Package']")
        if update_button is not None and update_button.element_to_be_clickable():
            update_button.execute_script("arguments[0].click();")
            return True
        return False

    def delete_package(self, package_name) -> bool:
        """Performs deletion of a package

        Args:
            package_name: Name of the package to be remove

        Returns: returns the result of delete operation

        """
        package_list = self.ui_element.find_elements_by_xpath("//div[@data-selenium-id='PackageRow']")
        if package_list is not None:
            for package in package_list:
                selected_package = package.text.split('\n')
                package_title = selected_package[1] if len(selected_package) > 0 else ''
                if package_title == package_name:
                    delete_button = package.find_element_by_xpath(".//div[@data-selenium-id='PackageActions']/button[2]")
                    if delete_button is not None:
                        delete_button.execute_script("arguments[0].click();")
                        return True
        return False

    def delete_all_packages(self) -> bool:
        """Performs deletion of all packages

        Returns: returns the result of delete operation

        """
        multi_select_checkbox = self.get_locator(LocatorType.XPath, "//div[@class='PackageHeader__multiselect']/button")
        if multi_select_checkbox is not None and multi_select_checkbox.element_to_be_clickable():
            multi_select_checkbox.execute_script("arguments[0].click();")
            element = "//button[contains(text(),'Delete')]"
            check_element = self.check_element_presence(LocatorType.XPath, element, 20)
            if check_element:
                # Delete button element is located in the index number 1
                delete_button = self.ui_element.find_elements_by_xpath("//button[contains(text(),'Delete')]")[1]
                if delete_button is not None:
                    delete_button.execute_script("arguments[0].click();")
                    return True
        return False

    def check_package(self, package_details: tuple) -> bool:
        """Check for a package and it's version

        Args:
            package_details: Name of the package

        Returns: returns the result of check verify package

        """
        # TODO: write a separate method for package comparison while testing in safari
        package_list = self.ui_element.find_elements_by_xpath("//div[@data-selenium-id='PackageRow']")
        if package_list is not None:
            # Iterate through page elements
            for package in package_list:
                package_detail = package.text.split('\n')
                package_name = package_detail[1]
                package_version = package_detail[3]
                # Compare package-details on page with the package-details from argument
                if not package_details.version.strip():
                    if package_name == package_details.name.strip():
                        return True
                else:
                    if package_name == package_details.name.strip() and package_version == package_details.version.strip():
                        return True
        return False

    def click_advanced_configuration_settings(self) -> bool:
        """Performs click action on Advanced configuration settings

        Returns: returns the result of click action

        """
        element = "//button[contains(text(),'Advanced Configuration Settings')]"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            configuration_button = self.get_locator(LocatorType.XPath, element)
            configuration_button.execute_script("arguments[0].click();")
            return True
        return False

    def click_edit_dockerfile_button(self) -> bool:
        """Performs click action on edit dockerfile button

        Returns: returns the result of click action

        """
        element = "//button/span[contains(text(),'Edit Dockerfile')]"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            dockerfile_button = self.get_locator(LocatorType.XPath, element)
            dockerfile_button.execute_script("arguments[0].click();")
            return True
        return False

    def click_and_input_docker_text_area(self, command) -> bool:
        """Performs click action and input command to docker text area

        Args:
            command: Command to be executed

        Returns: returns the result of command input action

        """
        element = f"//textarea[@placeholder='Enter dockerfile commands here']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            docker_text_area = self.get_locator(LocatorType.XPath, element)
            docker_text_area.execute_script("arguments[0].click();")
            docker_text_area.send_keys(command)
            return True
        return False

    def click_save_button(self) -> bool:
        """Performs click action on save button

        Returns: return the result of click action

        """
        element = "//button[contains(text(),'Save')]"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            save_button = self.get_locator(LocatorType.XPath, element)
            if save_button.element_to_be_clickable():
                save_button.execute_script("arguments[0].click();")
            return True
        return False

    def scroll_to_advanced_configuration(self) -> bool:
        """Scroll down the window to Advanced configuration settings button

        Returns: returns the result of scroll action

        """
        element = "//button[contains(text(),'Advanced Configuration Settings')]"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            save_button = self.get_locator(LocatorType.XPath, element)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            return True
        return False

    def check_rebuild_required(self) -> bool:
        """Performs checking for rebuild required

        Returns: returns the result of check element

        """
        element = "//div[@class='ContainerStatus__container-state Rebuild Tooltip-data']"
        check_element = self.check_element_presence(LocatorType.XPath, element, 20)
        if check_element:
            return True
        return False

    def scroll_to_add_package_button(self) -> bool:
        """Scroll down the window to add package button

        Returns: returns the result of scroll action

        """
        if self.add_package_button is not None:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", self.add_package_button)
            return True
        return False

    def check_build_modal_fail(self) -> bool:
        """Check for build modal fail

        Returns: returns the result of build modal monitor

        """
        element = "//p[contains(text(),'Environment Build Failed')]"
        check_element = self.check_element_presence(LocatorType.XPath, element, 60)
        if check_element:
            return True
        return False

    def click_modal_close_button(self) -> bool:
        """Performs click action on modal close button

        Returns: returns the result of click action

        """
        modal_close_button_element = "//button[@class='Btn Btn--flat Modal__close padding--small ']"
        if self.check_element_presence(LocatorType.XPath, modal_close_button_element, 20):
            modal_close_button = self.get_locator(LocatorType.XPath, modal_close_button_element)
            modal_close_button.execute_script("arguments[0].click();")
            return True
        return False

    def clear_docker_text_area(self) -> bool:
        """Clear docker text area

        Returns: returns the result of clear action

        """
        element = f"//textarea[@placeholder='Enter dockerfile commands here']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            docker_text_area = self.get_locator(LocatorType.XPath, element)
            docker_text_area.execute_script("arguments[0].click();")
            docker_text_area.clear_text()
            docker_text_area.send_keys(Keys.SPACE)
            return True
        return False

    def input_sensitive_file(self, file_name, file_content) -> bool:
        """ Input sensitive file

        Args:
            file_name: Name of the sensitive file
            file_content: Content of the sensitive file

        Returns: returns the result of file input

        """
        input_element = "//input[@id='add_secret']"
        if self.check_element_presence(LocatorType.XPath, input_element, 20):
            file_input = self.driver.find_element_by_id('add_secret')
            if file_input:
                temp_dir = tempfile.gettempdir()
                with open(os.path.join(temp_dir, file_name), 'w') as temp_file:
                    temp_file.write(file_content)
                file_path = os.path.join(temp_dir, file_name)
                file_input.send_keys(file_path)
                return True
        return False

    def add_destination_directory(self, directory_name) -> bool:
        """ Input sensitive file

        Args:
            directory_name: Name of the destination directory

        Returns: returns the result of input action

        """
        input_element = "//input[@id='secret_path']"
        if self.check_element_presence(LocatorType.XPath, input_element, 20):
            destination_input = self.get_locator(LocatorType.XPath, input_element)
            if destination_input is not None:
                destination_input.send_keys(directory_name)
                return True
        return False

    def click_sensitive_file_save_button(self) -> bool:
        """ CLick on sensitive file save button

        Returns: returns the result of click action

        """
        save_button_element = "//button[contains(text(),'Save')]"
        if self.check_element_presence(LocatorType.XPath, save_button_element, 20):
            save_button = self.get_locator(LocatorType.XPath, save_button_element)
            if save_button is not None:
                save_button.click()
                return True
        return False

    def click_edit_sensitive_file_button(self) -> bool:
        """ Performs click action on edit sensitive file button

        Returns: returns the result of click action

        """
        edit_button_element = "//button[@class='Btn Btn--medium Btn--noMargin Btn--round Btn__edit-secondary " \
                              "Btn__edit-secondary--medium']"
        if self.check_element_presence(LocatorType.XPath, edit_button_element, 20):
            edit_button = self.get_locator(LocatorType.XPath, edit_button_element)
            if edit_button is not None:
                edit_button.click()
                return True
        return False

    def replace_sensitive_file(self, file_name, file_content) -> bool:
        """ Input sensitive file

        Args:
            file_name: Name of the sensitive file
            file_content: Content of the sensitive file

        Returns: returns the result of file input

        """
        input_element = "//input[@id='update_secret']"
        if self.check_element_presence(LocatorType.XPath, input_element, 20):
            file_input = self.driver.find_element_by_id('update_secret')
            if file_input:
                temp_dir = tempfile.gettempdir()
                with open(os.path.join(temp_dir, file_name), 'w') as temp_file:
                    temp_file.write(file_content)
                file_path = os.path.join(temp_dir, file_name)
                file_input.send_keys(file_path)
                return True
        return False

    def scroll_to_page_top(self) -> bool:
        """Scroll to the window top

        Returns: returns the result of scroll action

        """
        return self.scroll_to_window_top()

    def verify_sensitive_file_is_missing(self) -> bool:
        """ Verify sensitive file is missing or not

        Returns: returns the result of verification

        """
        element = "//button[@data-selenium-id='SecretsPresent']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            sensitive_file_missing_element = self.get_locator(LocatorType.XPath, element)
            if sensitive_file_missing_element is not None:
                return True
        return False

    def click_sensitive_file_delete_button(self) -> bool:
        """ Performs click action on sensitive file delete button

        Returns: returns the result of click action

        """
        element = "//button[@class='Btn Btn--medium Btn--noMargin Btn--round Btn__delete-secondary " \
                  "Btn__delete-secondary--medium']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            delete_button = self.get_locator(LocatorType.XPath, element)
            if delete_button is not None:
                delete_button.click()
                return True
        return False

    def click_sensitive_file_delete_yes_button(self) -> bool:
        """ Performs click action on sensitive file delete yes button

        Returns: returns the result of click action

        """
        element = "//button[@class='Secrets__btn--round Secrets__btn--add']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            delete_yes_button = self.get_locator(LocatorType.XPath, element)
            if delete_yes_button is not None:
                delete_yes_button.click()
                return True
        return False

    def verify_sensitive_file_is_added(self, file_name) -> bool:
        """ Verify sensitive file is added or not

        Returns: returns the result of verification

        """
        element = "//div[@class='SecretsTable__name']"
        if self.check_element_presence(LocatorType.XPath, element, 20):
            sensitive_file_text = self.get_locator(LocatorType.XPath, element).text
            if sensitive_file_text is not None and sensitive_file_text == file_name:
                return True
        return False
