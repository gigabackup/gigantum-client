from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
from framework.factory.models_enums.constants_enums import LocatorType
from framework.factory.models_enums.constants_enums import CompareUtilityType
from selenium.webdriver.remote.webelement import WebElement


class AddPackageComponent(BaseComponent):
    """ Represents the components while adding new packages.

    Holds a set of all locators for add package. Handles events and test functions of adding packages
    """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(AddPackageComponent, self).__init__(driver, component_data)
        self.package_title_input = self.get_locator(LocatorType.XPath, "//input[@class='AddPackageForm__input']")
        self.add_package = self.get_locator(LocatorType.XPath, "//button[@class='Btn Btn__add']")

    def input_package_name(self, package_name: str) -> bool:
        """Input action for package name

        Args:
            package_name: Name of the package

        Returns: returns the result of input action

        """
        if self.package_title_input is not None:
            self.package_title_input.send_keys(package_name)
            return True
        return False

    def click_add_button(self) -> bool:
        """Performs the click action on add button

        Returns: returns the result of click action

        """
        if self.add_package is not None:
            self.add_package.click()
            return True
        return False

    def verify_package_and_version(self, package: tuple) -> bool:
        """Performs verification of package and it's corresponding version

        Args:
            package: Tuple with package name and it's version

        Returns: returns the result of comparison

        """
        if self.check_element_presence(LocatorType.XPath, "//div[@class='PackageQueue__validCount flex "
                                                          "justify--right align-items--center']",
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            div_package_details = self.ui_element.find_elements_by_xpath("//div[@class='PackageQueue__row "
                                                                         "flex align-items--center justify--right']")
            if div_package_details is not None:
                for package_detail in div_package_details:
                    if self.__compare_package(package, package_detail):
                        return True
        return False

    def input_package_version(self, version: str) -> bool:
        """Performs input action of package name and version

        Args:
            version: Version of the package

        Returns: returns the result of input action

        """
        package_version_radio_btn = self.get_locator(LocatorType.XPath, "//div[@class='AddPackageForm__version "
                                                                        "flex align-items--center']/label[2]"
                                                                        "/span[contains(text(),'Specify')]")
        package_version_input = self.get_locator(LocatorType.XPath, "//div[@class='AddPackageForm__version "
                                                                    "flex align-items--center']/label[2]/input[2]")
        if package_version_radio_btn is not None:
            package_version_radio_btn.click()
            if package_version_input is not None:
                package_version_input.send_keys(version)
                return True
        return False

    def click_install_all_packages(self) -> bool:
        """Performs the click action on install all button

        Returns: returns the result of click action

        """
        install_all_button = self.get_locator(LocatorType.XPath, "//button[contains(text(),'Install All')]")
        if install_all_button.element_to_be_clickable():
            install_all_button.click()
            return True
        return False

    def verify_package_list(self, package_details_list: list) -> bool:
        """Verify all packages

        Args:
            package_details_list: Details of packages

        Returns: returns the comparison result

        """
        if self.check_element_presence(LocatorType.XPath, "//div[@class='PackageQueue__validCount flex "
                                                          "justify--right align-items--center']",
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            div_package_details = self.ui_element.find_elements_by_xpath("//div[@class='PackageQueue__row "
                                                                         "flex align-items--center justify--right']")
            if div_package_details is not None:
                for index, packages_arg in enumerate(package_details_list):
                    if not self.__compare_package(packages_arg, div_package_details[index]):
                        return False
        return True

    def monitor_package_list_status(self, compare_text: str, wait_timeout: int) -> bool:
        """Monitors the text in the div of the component with the value in arg

        Args:
            compare_text: The text to compare with.
            wait_timeout: Time period for which the wait should continue

        Returns:
            Returns the comparison result.
        """
        if self.check_element_presence(LocatorType.XPath, "//div[@class='PackageQueue__validCount flex "
                                                          "justify--right align-items--center']",
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            package_status_element = self.ui_element.find_element_by_xpath("//div[@class='PackageQueue__validCount flex"
                                                                           " justify--right align-items--center']")
            compared_value = package_status_element.wait_until(CompareUtilityType.CompareText, wait_timeout,
                                                               compare_text)
            return compared_value

    def __compare_package(self, package: tuple, package_detail: WebElement):
        """Performs comparison of package details from argument with package details in div element

        Args:
            package: package detail from argument
            package_detail: package detail from div element

        Returns: Returns the comparison result

        """
        agent = self.driver.capabilities['browserName']
        package_detail_split = package_detail.text.split('\n')
        if len(package_detail_split) > 0:
            if agent.lower() in ['chrome', 'firefox']:
                package_name, package_version = package_detail_split[1].strip(), package_detail_split[2].strip()
                # Compare package-details on UI with the package-details from argument
                if package_name == package.name and package_version == package.version:
                    return True
            elif agent.lower() == 'safari':
                # Safari returns a single string with no delimiters so check in a less strict way
                # by just seeing if the name and version are in the string
                if package.name in package_detail_split[0] and package.version in package_detail_split[0]:
                    return True
            else:
                raise ValueError(f"Unsupported browser type while verifying package version: {agent}")
        return False

    def click_requirements_tab(self) -> bool:
        """Performs the click action on Add requirements tab

        Returns: returns the result of click action

        """
        requirement_tab = self.get_locator(LocatorType.XPath, "//h5[contains(text(),'Add Requirements File')]")
        if requirement_tab.element_to_be_clickable():
            requirement_tab.click()
            return True
        return False

    def drag_and_drop_text_file(self, packages: list) -> bool:
        """Drag and drop the requirements file

        Args:
            packages: Name of packages to be installed

        Returns: returns the result of drag and drop action

        """
        drop_box = self.get_locator(LocatorType.XPath, "//div[@class='Dropbox flex flex--column align-items--center']")
        if drop_box is not None:
            # Create a new string by adding new line character to each package in the packages list
            package_str = "\n".join(packages)
            drop_box.drag_drop_file_in_drop_zone(file_content=package_str)
            return True
        return False

    def choose_package_manager_from_dropdown(self, package_manager) -> bool:
        """ Select package manager from drop down list

        Args:
            package_manager: Name of the package manager to be selected from the drop down list

        Returns: returns the result of selection

        """
        drop_down_element = "//div[@data-selenium-id='Dropdown']"
        if self.check_element_presence(LocatorType.XPath, drop_down_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            drop_down_field = self.get_locator(LocatorType.XPath, drop_down_element)
            drop_down_field.execute_script("arguments[0].click();")
            menu_item_element = f"//li[contains(text(),'{package_manager}')]"
            if self.check_element_presence(LocatorType.XPath, menu_item_element,
                                           GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
                menu_item = self.get_locator(LocatorType.XPath, menu_item_element)
                if menu_item is not None:
                    menu_item.execute_script("arguments[0].click();")
                    return True
        return False

    def click_cancel_build_button(self) -> bool:
        """Performs the click action on cancel build button

        Returns: returns the result of click action

        """
        cancel_build_button = self.get_locator(LocatorType.XPath, "//button[@class='Btn Btn--inverted "
                                                                  "align-self--end']")
        if cancel_build_button.element_to_be_clickable():
            cancel_build_button.click()
            return True
        return False

    def check_build_failed(self) -> bool:
        """Check whether the build is failed or not

        Returns: returns the result of build failed checking

        """
        cancel_build_button_element = "//div[@class='ProgressLoader__progress ProgressLoader__progress--failed']"
        if self.check_element_presence(LocatorType.XPath, cancel_build_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_clear_cache_and_build_button(self) -> bool:
        """Performs the click action on cancel build button

        Returns: returns the result of click action

        """
        cancel_build_button = self.get_locator(LocatorType.XPath, "//button[@class='Btn--inverted align-self--end']")
        if cancel_build_button.element_to_be_clickable():
            cancel_build_button.click()
            return True
        return False
