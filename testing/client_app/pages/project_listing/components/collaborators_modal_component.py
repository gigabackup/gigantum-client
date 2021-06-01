from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType, CompareUtilityType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class CollaboratorsModalComponent(BaseComponent):
    """ Represents one of the components of project listing page.

       Holds a set of all locators within the collaborators modal on the project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(CollaboratorsModalComponent, self).__init__(driver, component_data)

    def add_collaborator(self, collaborator_name) -> bool:
        """ Add collaborator into input area

        Args:
            collaborator_name: Name of the collaborator

        Returns: returns the result of input action

        """
        element = "//input[@placeholder='Add Collaborator']"
        collaborator_input_area = self.get_locator(LocatorType.XPath, element)
        if collaborator_input_area is not None:
            collaborator_input_area.send_keys(collaborator_name)
            return True
        return False

    def select_collaborator_permission(self, collaborator_permission) -> bool:
        """ Select collaborator permission from drop down

        Args:
            collaborator_permission: Collaborator permission

        Returns: returns the result of selection

        """
        element = "//span[@class='CollaboratorModal__PermissionsSelector Dropdown CollaboratorModal__" \
                  "PermissionsSelector--add Dropdown--collapsed']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            drop_down_element = self.get_locator(LocatorType.XPath, element)
            drop_down_element.click()
            element = f"//li/div[contains(text(), '{collaborator_permission}')]"
            if self.check_element_presence(LocatorType.XPath, element, 30):
                admin_menu = self.get_locator(LocatorType.XPath, element)
                admin_menu.click()
                return True
        return False

    def click_add_collaborator_button(self) -> bool:
        """ Performs click event on add collaborator button

        Returns: returns the result of click action

        """
        element = "//button[@data-selenium-id='ButtonLoader']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            btn_add_collaborator = self.get_locator(LocatorType.XPath, element)
            btn_add_collaborator.click()
            return True
        return False

    def verify_collaborator_is_listed(self, collaborator_name) -> bool:
        """ Verify collaborator is listed in the modal

        Args:
            collaborator_name: Name of the collaborator

        Returns: returns the result of verification

        """
        element = f"//li/div[contains(text(), '{collaborator_name}')]"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            return True
        return False

    def click_collaborator_modal_close(self) -> bool:
        """ Performs click action on collaborator modal close

        Returns: returns the result of click action

        """
        element = "//button[@class='Btn Btn--flat Modal__close padding--small ']"
        btn_close_collaborator = self.get_locator(LocatorType.XPath, element)
        if btn_close_collaborator is not None:
            btn_close_collaborator.click()
            return True
        return False

    def click_collaborator_publish_button(self) -> bool:
        """ Performs click action on collaborator modal publish button

        Returns: returns the result of click action

        """
        element = "//button[@class='Btn Btn--inverted NoCollaborators__button--publish']"
        if self.check_element_presence(LocatorType.XPath, element, 30):
            publish_button = self.get_locator(LocatorType.XPath, element)
            if publish_button is not None:
                publish_button.click()
                return True
        return False

    def update_collaborator_permission(self, collaborator_name: str, collaborator_permission: str) -> bool:
        """ Update collaborator permission

        Args:
            collaborator_name: Name of the collaborator
            collaborator_permission: Collaborator permission

        Returns: returns the result of update action

        """
        element = "//li[@data-selenium-id='CollaboratorsRowx']"
        if self.check_element_presence(LocatorType.XPath, element, 40):
            collaborators_list = self.driver.find_elements_by_xpath(element)
            for collaborators in collaborators_list:
                if collaborators is not None:
                    collaborator_title_div = collaborators.find_element_by_xpath\
                        (".//div[@class='CollaboratorsModal__collaboratorName']")
                    if collaborator_name == collaborator_title_div.get_text().strip():
                        collaborator_permission_drop_down = collaborators.find_element_by_xpath\
                            (".//div[@class='CollaboratorsModal__permissions "
                             "CollaboratorsModal__permissions--individual CollaboratorsModal__permissions--small']")
                        if collaborator_permission_drop_down is not None:
                            collaborator_permission_drop_down.click()
                            collaborator_permission_element = f".//li/div[contains(text(), '{collaborator_permission}')]"
                            is_permissions_loaded = collaborator_permission_drop_down.wait_until\
                                (CompareUtilityType.CheckElement, 30, collaborator_permission_element)
                            if is_permissions_loaded:
                                collaborator_permission_div = collaborator_permission_drop_down.find_element_by_xpath\
                                    (collaborator_permission_element)
                                if collaborator_permission_div is not None:
                                    collaborator_permission_div.click()
                                    delete_button_xpath = ".//div[@class='ButtonLoader__icon hidden']"
                                    is_collaborator_updated = collaborators.wait_until(CompareUtilityType.CheckElement, 30,
                                                                                       delete_button_xpath)
                                    if is_collaborator_updated:
                                        return True
        return False

