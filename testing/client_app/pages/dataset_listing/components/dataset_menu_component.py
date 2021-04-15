from framework.base.component_base import BaseComponent
from framework.factory.models_enums.constants_enums import LocatorType
from selenium import webdriver
from framework.factory.models_enums.page_config import ComponentModel
import tempfile
import os
import random
from pathlib import Path
import string
import time


class DatasetMenuComponent(BaseComponent):
    """ Represents one of the components of dataset listing page.

       Holds a set of all locators within the menu components on the dataset listing page of
       gigantum client as an entity. Handles events and test functions of locators
       in this entity.
       """

    def __init__(self, driver: webdriver, component_data: ComponentModel) -> None:
        super(DatasetMenuComponent, self).__init__(driver, component_data)

    def click_data_tab(self) -> bool:
        """Click action on data tab"""
        element = "//li[@id='data']"
        create_button = self.get_locator(LocatorType.XPath, element)
        if create_button is not None:
            create_button.click()
            return True
        return False

    def click_datasets_menu(self) -> bool:
        """Performs click action on datasets menu

        Returns: returns the result of click action

        """
        element = "//a[contains(text(), 'Datasets')]"
        datasets_menu = self.get_locator(LocatorType.XPath, element)
        if datasets_menu is not None:
            datasets_menu.click()
            # DMK NOTE: the 'Create New' button is duplicated now on the Project and Dataset pages. If we don't wait a
            # tiny bit here, when switching between pages, you can sometimes get a stale ref to the button.
            time.sleep(.25)
            return True
        return False

    def click_delete_dataset_menu(self) -> bool:
        """Performs click action on delete dataset menu

        Returns: returns the result of click action

        """
        element = "//button[contains(text(), 'Delete Dataset')]"
        menu_dataset_delete = self.get_locator(LocatorType.XPath, element)
        if menu_dataset_delete is not None:
            menu_dataset_delete.click()
            return True
        return False
