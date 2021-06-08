from framework.base.page_base import BasePage
from framework.factory.models_enums.page_config import PageConfig
from framework.factory.models_enums.page_config import ComponentModel
from client_app.pages.dataset_listing.components.dataset_menu_component import DatasetMenuComponent
from client_app.pages.dataset_listing.components.dataset_listing_component import DatasetListingComponent
from client_app.pages.dataset_listing.components.dataset_data_component import DatasetDataComponent
from client_app.pages.project_listing.components.project_menu_component import ProjectMenuComponent
from client_app.pages.dataset_listing.components.dataset_delete_component import DatasetDeleteComponent
from client_app.pages.project_listing.components.server_component import ServerComponent
from client_app.pages.project_listing.components.project_code_input_output_data_component import \
    ProjectCodeInputOutputDataComponent
from client_app.pages.project_listing.components.project_container_status_component import \
    ProjectContainerStatusComponent
from client_app.pages.project_listing.components.project_listing_component import ProjectListingComponent
from client_app.pages.project_listing.components.collaborators_modal_component import CollaboratorsModalComponent


class DatasetListingPage(BasePage):
    """Represents the project-listing page of gigantum client.

    Holds the locators on the dataset-listing page of gigantum client. The locators can be
    presented in its corresponding component or directly on the page. Test functions can
    use these objects for all activities and validations and can avoid those in the
    test functions.
    """

    def __init__(self, driver) -> None:
        page_config = PageConfig()
        super(DatasetListingPage, self).__init__(driver, page_config)
        self.component_model = ComponentModel()
        self._dataset_menu_component = None
        self._dataset_listing_component = None
        self._dataset_data_component = None
        self._project_menu_component = None
        self._dataset_delete_component = None
        self._server_component = None
        self._code_input_output_data_component = None
        self._container_status_component = None
        self._project_listing_component = None
        self._collaborator_modal_component = None

    @property
    def dataset_menu_component(self) -> DatasetMenuComponent:
        """ Returns an instance of dataset menu component."""
        if self._dataset_menu_component is None:
            self._dataset_menu_component = DatasetMenuComponent(self.driver, self.component_model)
        return self._dataset_menu_component

    @property
    def dataset_listing_component(self) -> DatasetListingComponent:
        """ Returns an instance of dataset listing component."""
        if self._dataset_listing_component is None:
            self._dataset_listing_component = DatasetListingComponent(self.driver, self.component_model)
        return self._dataset_listing_component

    @property
    def dataset_data_component(self) -> DatasetDataComponent:
        """ Returns an instance of dataset data component."""
        if self._dataset_data_component is None:
            self._dataset_data_component = DatasetDataComponent(self.driver, self.component_model)
        return self._dataset_data_component

    @property
    def project_menu_component(self) -> ProjectMenuComponent:
        """ Returns an instance of project menu component."""
        if self._project_menu_component is None:
            self._project_menu_component = ProjectMenuComponent(self.driver, self.component_model)
        return self._project_menu_component

    @property
    def dataset_delete_component(self) -> DatasetDeleteComponent:
        """ Returns an instance of dataset delete component."""
        if self._dataset_delete_component is None:
            self._dataset_delete_component = DatasetDeleteComponent(self.driver, self.component_model)
        return self._dataset_delete_component

    @property
    def server_component(self) -> ServerComponent:
        """ Returns an instance of server component."""
        if self._server_component is None:
            self._server_component = ServerComponent(self.driver, self.component_model)
        return self._server_component

    @property
    def code_input_output_data_component(self) -> ProjectCodeInputOutputDataComponent:
        """ Returns an instance of code input output data component."""
        if self._code_input_output_data_component is None:
            self._code_input_output_data_component = ProjectCodeInputOutputDataComponent(self.driver, self.component_model)
        return self._code_input_output_data_component

    @property
    def container_status_component(self) -> ProjectContainerStatusComponent:
        """ Returns an instance of container status component."""
        if self._container_status_component is None:
            self._container_status_component = ProjectContainerStatusComponent(self.driver)
        return self._container_status_component

    @property
    def project_listing_component(self) -> ProjectListingComponent:
        """ Returns an instance of code input output data component."""
        if self._project_listing_component is None:
            self._project_listing_component = ProjectListingComponent(self.driver, self.component_model)
        return self._project_listing_component

    @property
    def collaborator_modal_component(self) -> CollaboratorsModalComponent:
        """ Returns an instance of code input output data component."""
        if self._collaborator_modal_component is None:
            self._collaborator_modal_component = CollaboratorsModalComponent(self.driver, self.component_model)
        return self._collaborator_modal_component
