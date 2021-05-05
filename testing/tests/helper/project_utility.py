import random
import time
from client_app.pages.project_listing.project_listing_page import ProjectListingPage
from selenium import webdriver
from tests.constants_enums.constants_enums import ProjectConstants
from client_app.pages.jupyter_lab.jupyter_lab_page import JupyterLabPage
import string


class ProjectUtility:
    def create_project(self, driver: webdriver, is_guide: bool = True) -> str:
        """Logical separation of create package functionality"""
        # Create a project
        # Load Project Listing Page
        project_list = ProjectListingPage(driver)
        if not project_list:
            return "Could not load Project Listing Page"

        if is_guide:
            # Closes the guide
            is_guide_close_msg = self.close_guide(project_list)
            if is_guide_close_msg != ProjectConstants.SUCCESS.value:
                return is_guide_close_msg

        # Click on "Create New"
        is_clicked = project_list.click_create_button()
        if not is_clicked:
            return "Could not click Create New"

        # Enter project title-(unique random name) and description
        # UUID is not given now, since it creates big string
        # This can be changed along with upcoming  text cases
        rand_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        project_title = f"p-{rand_string}"
        is_project_title_typed = project_list.type_project_title(project_title)
        is_project_desc_typed = project_list.type_new_project_desc_textarea(f"{project_title} -> Description ")
        if not is_project_title_typed:
            return "Could not type project title"
        if not is_project_desc_typed:
            return "Could not type project description"

        # Click "Continue"
        is_submitted = project_list.click_submit_button()
        if not is_submitted:
            return "Could not click Continue button to create new project"

        # Select the "Python3 Minimal" Base
        is_base_option_clicked = project_list.click_python3_minimal_stage()
        if not is_base_option_clicked:
            return "Could not click option-python3_minimal_stage"

        # Click "Create Project"
        is_submitted = project_list.click_submit_button()
        if not is_submitted:
            return "Could not click Create Project button after Base select"

        # Monitor container status to go to building state
        is_status_changed = project_list.monitor_container_status("Building", 60)
        if not is_status_changed:
            return "Could not get Building status"

        # Monitor container status to go through building -> stopped state
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        if not is_status_changed:
            return "Could not get Stopped status"

        return ProjectConstants.SUCCESS.value

    def close_guide(self, project_list) -> str:
        """ Logical separation of closing the guide after log in

        Args:
            project_list: The page with UI elements
        """
        is_guide_active = project_list.is_active_helper_guide_slider()
        if is_guide_active:
            is_clicked = project_list.click_got_it_button()
            if not is_clicked:
                return "Could not click got it button"

            is_clicked = project_list.click_helper_guide_slider()
            if not is_clicked:
                return "Could not click helper guide slider"

            is_clicked = project_list.click_helper_close_button()
            if not is_clicked:
                return "Could not click helper close button"
        return ProjectConstants.SUCCESS.value

    def verify_command_execution(self, driver: webdriver, commands_list: list, is_only_exist: bool = False) -> str:
        """ Logical separation of verify package using jupyter

        Args:
            driver: webdriver instance
            is_only_exist: Decision variable to determine whether only the expected output exist
            commands_list: List of tuples with commands, output and verification message
        """
        # Load Project Package Page
        jupyter_lab_page = JupyterLabPage(driver)
        if not jupyter_lab_page:
            return "Could not load Project Listing Page"

        # Check package installation using jupyter
        is_clicked = jupyter_lab_page.click_jupyterlab_div()
        if not is_clicked:
            return "Could not click Jupyter Lab button"

        # Wait for new tab to open with new url
        is_url_loaded = jupyter_lab_page.wait_for_url_in_new_tab("lab/tree/code", 1, 80)
        if not is_url_loaded:
            return "Could not open new window"

        # Click Python3 under notebook
        is_clicked = jupyter_lab_page.click_python3_notebook()
        if not is_clicked:
            return "Could not click python3 under notebook"

        # Get python3 notebook title
        python3_notebook_title = jupyter_lab_page.get_python3_notebook_title()
        if python3_notebook_title is None:
            return "Could not get python3 notebook title"

        # Iterate through list of commands
        for index, command in enumerate(commands_list):
            # Join all commands and create a command string
            command_input_str = '\n'.join(command.command_text)

            # Type command string to the input textarea
            command_typed = jupyter_lab_page.type_command(command_input_str, index+1)
            if not command_typed:
                return "Could not type the commands"

            # Execution of command
            is_clicked = jupyter_lab_page.click_run_cell()
            if not is_clicked:
                return "Could not click run for command"

            # Verification of command output
            if not is_only_exist:
                jupyter_notebook_output = jupyter_lab_page.is_jupyter_notebook_output_exist(command.output, index+1)
            else:
                jupyter_notebook_output = jupyter_lab_page.is_jupyter_notebook_output_only_exist(
                    command.output, index+1)
            # Return message if output verification is failed
            if not jupyter_notebook_output:
                return command.error_message

        jupyter_lab_page.close_tab(f"lab/tree/code/{python3_notebook_title}", 0)

        # Click on container status button to stop container
        is_clicked = jupyter_lab_page.click_container_status()
        if not is_clicked:
            return "Could not click container status"

        # Monitor container status to go through running -> stopped
        jupyter_lab_page.move_to_element()
        is_status_changed = jupyter_lab_page.monitor_container_status("Stopped", 60)
        if not is_status_changed:
            return "Could not get Stopped status"

        return ProjectConstants.SUCCESS.value

    def delete_project(self, driver: webdriver) -> str:
        """ Logical separation of delete project functionality

        Args:
            driver: webdriver instance
        """
        # Delete a local project
        # Load Project Listing Page
        project_list = ProjectListingPage(driver)
        if not project_list:
            return "Could not load Project Listing Page"

        # Click project menu button
        is_clicked = project_list.project_menu_component.click_project_menu_button()
        if not is_clicked:
            return "Could not click project menu button"

        # Click delete project menu
        is_checked = project_list.project_menu_component.click_delete_project_menu()
        if not is_checked:
            return "Could not click delete project menu"

        # Get project title from delete project window
        project_title = project_list.project_delete_component.get_project_title()
        if project_title is None:
            return "Could not get project title"

        # Input project title
        is_typed = project_list.project_delete_component.input_project_title(project_title)
        if not is_typed:
            return "Could not type project title"

        # Click delete project button
        is_clicked = project_list.project_delete_component.click_delete_button()
        if not is_clicked:
            return "Could not click delete project button"

        # Check delete window closed
        is_checked = project_list.project_delete_component.check_delete_window_closed()
        if not is_checked:
            return "Delete project window is not closed"

        return ProjectConstants.SUCCESS.value

    def publish_project(self, driver: webdriver):
        """Logical separation of publish project functionality

        Args:
            driver: webdriver instance
        """
        # Load Project Listing Page
        project_list = ProjectListingPage(driver)
        if not project_list:
            return "Could not load Project Listing Page"

        # Time sleep to make sure that the publish button is loaded
        time.sleep(1)

        # Click on project publish button
        is_clicked = project_list.project_menu_component.click_publish_button()
        if not is_clicked:
            return "Could not click project publish button"

        # Enable private mode in project publish window
        is_enabled = project_list.project_menu_component.enable_private_mode()
        if not is_enabled:
            return "Could not enable private mode in project publish window"

        # Click on publish button on publish window
        is_clicked = project_list.project_menu_component.click_publish_window_button()
        if not is_clicked:
            return "Could not click project publish button on project publish window"

        # Monitor container status to go through Stopped -> Publishing
        is_status_changed = project_list.monitor_container_status("Publishing", 60)
        if not is_status_changed:
            return "Could not get Publishing status"

        # Monitor container status to go through Publishing -> Stopped
        is_status_changed = project_list.monitor_container_status("Stopped", 60)
        if not is_status_changed:
            return "Could not get Stopped status"

        # Check private lock icon presence
        is_checked = project_list.project_menu_component.check_private_lock_icon_presence()
        if not is_checked:
            return "Could not found private lock icon presence"

        return ProjectConstants.SUCCESS.value
