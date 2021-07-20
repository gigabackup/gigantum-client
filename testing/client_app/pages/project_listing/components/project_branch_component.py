from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from client_app.constant_enums.constants_enums import GigantumConstants
from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType, CompareUtilityType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel


class ProjectBranchComponent(BaseComponent):
    """ Represents one of the components of project branch component.

       Holds a set of all locators of branch component in project listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(ProjectBranchComponent, self).__init__(driver, component_data)
        self.branch_dropdown_element = "//div[@class='BranchDropdown__text']"
        self.manage_branches_button_element = "//div[@class='BranchDropdown__menu']/div/button"

    def click_create_branch_icon(self) -> bool:
        """ Performs click action on create branch icon.

        Returns: returns the result of click action

        """
        create_branch_icon_element = "//button[@data-selenium-id='CreateBranchButtonx']"
        if self.check_element_presence(LocatorType.XPath, create_branch_icon_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            create_branch_button = self.get_locator(LocatorType.XPath, create_branch_icon_element)
            create_branch_button.click()
            return True
        return False

    def input_branch_name(self, branch_name: str) -> bool:
        """Input action for branch name

        Args:
            branch_name: Name of the branch

        Returns: returns the result of input action

        """
        branch_input_element = "//input[@id='CreateBranchName']"
        if self.check_element_presence(LocatorType.XPath, branch_input_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_input = self.get_locator(LocatorType.XPath, branch_input_element)
            branch_input.send_keys(branch_name)
            return True
        return False

    def input_branch_description(self, branch_description: str) -> bool:
        """Input action for branch description

        Args:
            branch_description: Branch description

        Returns: returns the result of input action

        """
        branch_description_input_element = "//textarea[@id='CreateBranchDescription']"
        if self.check_element_presence(LocatorType.XPath, branch_description_input_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_description_input = self.get_locator(LocatorType.XPath, branch_description_input_element)
            branch_description_input.set_text(branch_description)
            return True
        return False

    def click_create_branch_button(self) -> bool:
        """ Performs click action on create branch button.

        Returns: returns the result of click action

        """
        create_branch_button_element = "//button[@class='Btn ButtonLoader Btn--last']"
        if self.check_element_presence(LocatorType.XPath, create_branch_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            create_branch_button = self.get_locator(LocatorType.XPath, create_branch_button_element)
            if create_branch_button is not None and create_branch_button.element_to_be_clickable():
                create_branch_button.click()
                return True
        return False

    def verify_create_branch_window_closed(self) -> bool:
        """ Verify create branch window is closed or not.

        Returns: returns the result of verification

        """
        create_branch_window_element = "//div[@class='Modal__content Modal__content--large add']"
        if self.check_element_absence(LocatorType.XPath, create_branch_window_element,
                                      GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def get_current_branch(self) -> str:
        """ Fetch current branch title

        Returns: returns current branch title

        """
        if self.check_element_presence(LocatorType.XPath, self.branch_dropdown_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_div_text = self.get_locator(LocatorType.XPath, self.branch_dropdown_element)
            if branch_div_text is not None:
                return branch_div_text.get_text().strip()

    def switch_branch(self, branch_name) -> bool:
        """ Switch branch

        Args:
            branch_name: Name of the branch

        Returns: returns the result of branch switching

        """
        is_branch_dropdown_clicked = self.__click_branch_dropdown()
        if is_branch_dropdown_clicked:
            branch_dropdown_menu = self.__get_branch_dropdown_menu()
            if branch_dropdown_menu is not None:
                branch_list_item_element = f"//li[@class='BranchMenu__list-item']/div[contains(text(), '{branch_name}')]"
                branch_list_item = branch_dropdown_menu.find_element_by_xpath(branch_list_item_element)
                if branch_list_item is not None:
                    branch_list_item.click()
                    return True
        return False

    def __click_branch_dropdown(self) -> bool:
        """ Performs click action on branch dropdown

        Returns: returns the result of branch dropdown click action

        """
        if self.check_element_presence(LocatorType.XPath, self.branch_dropdown_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_div = self.get_locator(LocatorType.XPath, self.branch_dropdown_element)
            if branch_div is not None:
                branch_div.click()
                return True
        return False

    def __get_branch_dropdown_menu(self) -> WebElement:
        """ Get branch dropdown menu

        Returns: returns branch dropdown menu

        """
        branch_dropdown_menu_element = "//div[@class='BranchDropdown__menu']"
        if self.check_element_presence(LocatorType.XPath, branch_dropdown_menu_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_dropdown_menu = self.get_locator(LocatorType.XPath, branch_dropdown_menu_element)
            if branch_dropdown_menu is not None:
                return branch_dropdown_menu

    def click_manage_branches_button(self) -> bool:
        """ Performs click action on manage branches button.

        Returns: returns the result of click action

        """
        is_branch_dropdown_clicked = self.__click_branch_dropdown()
        if is_branch_dropdown_clicked:
            if self.check_element_presence(LocatorType.XPath, self.manage_branches_button_element,
                                           GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
                manage_branches_button = self.get_locator(LocatorType.XPath, self.manage_branches_button_element)
                if manage_branches_button:
                    manage_branches_button.click()
                    return True
        return False

    def move_to_branch(self, branch_name) -> bool:
        """ Moves  mouse focus to branch div element to highlight hidden elements

         Args:
            branch_name: Name of the branch

        Returns: returns the result of mouse move action

        """
        branch_text_element = f"//div[@class='Branches__branch']/div/div[1]/div[contains(text(), '{branch_name}')]"
        if self.check_element_presence(LocatorType.XPath, branch_text_element, 30):
            branch_div = self.get_locator(LocatorType.XPath, branch_text_element)
            ActionChains(self.driver).move_to_element(branch_div).perform()
        return True

    def click_branch_merge_button(self, branch_name) -> bool:
        """ Performs click action on create branch merge button.

        Args:
            branch_name: Name of the branch to be merge

        Returns: returns the result of click action

        """
        selected_branch_merge_button_element = "//div[@class='Branches__branch Branches__branch--selected " \
                                               "Branches__branch--active']/div/div[2]/button" \
                                               "[@class='BranchActions__btn Tooltip-data BranchActions__btn--merge']"
        if self.check_element_presence(LocatorType.XPath, selected_branch_merge_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            selected_branch_merge_button = self.get_locator(LocatorType.XPath, selected_branch_merge_button_element)
            if selected_branch_merge_button is not None:
                selected_branch_merge_button.click()
                return True
        return False

    def click_branch_merge_confirm_button(self) -> bool:
        """ Performs click action on branch merge confirm button.

        Returns: returns the result of click action

        """
        branch_merge_confirm_button_element = "//div[@class='ActionModal ActionModal--merge']/div[4]/button[2]"
        if self.check_element_presence(LocatorType.XPath, branch_merge_confirm_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_merge_confirm_button = self.get_locator(LocatorType.XPath, branch_merge_confirm_button_element)
            if branch_merge_confirm_button is not None:
                branch_merge_confirm_button.click()
                return True
        return False

    def click_branch_trash_icon_button(self, branch_name) -> bool:
        """ Performs click action on branch trash icon button.

        Args:
            branch_name: Name of the branch to be merge

        Returns: returns the result of click action

        """
        selected_branch_trash_icon_element = "//div[@class='Branches__branch Branches__branch--selected " \
                                             "Branches__branch--active']/div/div[2]/button[3]"
        if self.check_element_presence(LocatorType.XPath, selected_branch_trash_icon_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            selected_branch_trash_icon = self.get_locator(LocatorType.XPath, selected_branch_trash_icon_element)
            if selected_branch_trash_icon is not None:
                selected_branch_trash_icon.click()
                return True
        return False

    def click_branch_delete_local_checkbox(self) -> bool:
        """ Performs click action on branch delete local checkbox.

        Returns: returns the result of click action

        """
        branch_delete_local_checkbox_element = "//div[@class='ActionModal ActionModal--delete']" \
                                               "/div[3]/div/label[1]/input"
        if self.check_element_presence(LocatorType.XPath, branch_delete_local_checkbox_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            branch_delete_local_checkbox = self.get_locator(LocatorType.XPath, branch_delete_local_checkbox_element)
            if branch_delete_local_checkbox is not None:
                branch_delete_local_checkbox.click()
                return True
        return False

    def click_delete_branch_confirm_button(self) -> bool:
        """ Performs click action on delete branch confirm button.

        Returns: returns the result of click action

        """
        delete_branch_confirm_button_element = "//div[@class='ActionModal ActionModal--delete']/div[4]/button[2]"
        if self.check_element_presence(LocatorType.XPath, delete_branch_confirm_button_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            delete_branch_confirm_button = self.get_locator(LocatorType.XPath, delete_branch_confirm_button_element)
            if delete_branch_confirm_button is not None:
                delete_branch_confirm_button.click()
                return True
        return False

    def verify_branch_presence(self, branch_name) -> bool:
        """ Verify branch is present or not in branch dropdown.

        Returns: returns the result of branch verification

        """
        is_branch_dropdown_clicked = self.__click_branch_dropdown()
        if is_branch_dropdown_clicked:
            branch_dropdown_menu = self.__get_branch_dropdown_menu()
            if branch_dropdown_menu is not None:
                branch_list_item_element = ".//li[@class='BranchMenu__list-item']"
                branch_list_items = branch_dropdown_menu.find_elements_by_xpath(branch_list_item_element)
                for branch in branch_list_items:
                    branch_text_div = branch.find_element_by_xpath(".//div[@class='BranchMenu__text']")
                    if branch_text_div.get_text().strip() == branch_name:
                        return True
        return False

    def check_branch_switch_complete_pop_up_presence(self) -> bool:
        """ Check for the presence of branch switch complete pop up message

        Returns: returns True if the element is present

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def check_branch_switch_complete_pop_up_absence(self) -> bool:
        """ Check for the absence of branch switch complete pop up message

        Returns: returns True if the element is not present

        """
        element = "//p[@class='FooterMessage__title FooterMessage__title--collapsed']"
        switch_complete_pop_up = self.get_locator(LocatorType.XPath, element)
        if switch_complete_pop_up.invisibility_of_element_located(120):
            return True
        return False

    def check_create_branch_icon_presence(self) -> bool:
        """ Check for the create branch icon presence.

        Returns: returns the result of create branch icon presence checking

        """
        create_branch_icon_element = "//button[@data-selenium-id='CreateBranchButtonx']"
        if self.check_element_presence(LocatorType.XPath, create_branch_icon_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

    def click_manage_branches_menu_icon(self) -> bool:
        """ Performs click action on manage branches menu icon.

        Returns: returns the result of click action

        """
        manage_branches_menu_icon_element = "//button[@class='Btn--branch Btn--action ManageBranchButton Tooltip-data']"
        if self.check_element_presence(LocatorType.XPath, manage_branches_menu_icon_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            manage_branches_menu_icon = self.get_locator(LocatorType.XPath, manage_branches_menu_icon_element)
            if manage_branches_menu_icon:
                manage_branches_menu_icon.click()
                return True
        return False

    def click_create_branch_icon_in_manage_branches_menu(self) -> bool:
        """ Performs click action on create branch icon in manage branches menu.

        Returns: returns the result of click action

        """
        create_branch_icon_element = "//button[@class='BranchActions__btn BranchActions__btn--create']"
        if self.check_element_presence(LocatorType.XPath, create_branch_icon_element,
                                       GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            create_branch_icon = self.get_locator(LocatorType.XPath, create_branch_icon_element)
            if create_branch_icon:
                create_branch_icon.execute_script("arguments[0].click();")
                return True
        return False

    def verify_manage_branch_side_panel_is_opened(self) -> bool:
        """ Check for the presence of manage branch side panel

        Returns: returns True if the element is present

        """
        element = "//div[@class='BranchesSidePanel']"
        if self.check_element_presence(LocatorType.XPath, element, GigantumConstants.ELEMENT_PRESENCE_TIMEOUT.value):
            return True
        return False

